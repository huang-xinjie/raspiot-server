-- YS-NEC.lua

function initDevice()
    -- config wifi
    station_config = {}
    station_config.ssid = "what_the_hell"
    station_config.pwd = "daiguaCancan"
    print('Setting up WIFI...')
    wifi.setmode(wifi.STATION)
    wifi.sta.config(station_config)
    wifi.sta.connect()
    -- link ap
    tmr.alarm(1, 1000, tmr.ALARM_AUTO, function()
        if wifi.sta.getip() == nil then
            print('Waiting for IP ...')
        else
            print('IP is ' .. wifi.sta.getip())
            tmr.stop(1)
            times = 3
            sayHelloToManager(times)
        end
    end)
    --set up tcp server
    tcpS = net.createServer(net.TCP, 10)
    tcpC = nil
    -- set up uart
    uart.setup(0, 115200, 8, uart.PARITY_NONE, uart.STOPBITS_1, 0)
end

-- access in raspServer
function sayHelloToManager(times)
    if times == 0 then
        return false
    end
    json = build_json(wifi.sta.getip(), wifi.sta.getmac())
    srv = net.createConnection(net.TCP, 0)
    -- default manager port and ip
    srv:connect(22015, "172.20.10.6")
    srv:send(json)
    srv:on("receive", function(sck, c) 
        print(c) 
        recvJson = sjson.decode(c)
        if recvJson.response == 'Setup completed' then
            return true
        else 
            sayHelloToManager(times - 1)
        end
    end)
end

-- build device json to access in raspServer
function build_json(ip, uuid)
    msgtable = {}
    msgtable.ip = ip
    msgtable.uuid = uuid
    msgtable.device = "ys-nec"
    msgtable.identity = "device"
    msgtable.repository = "raspiot"
    msgtable.iotServer = "YS_NEC"
    
    ok, json = pcall(sjson.encode, msgtable)
    if ok then
        print(json)
        return json
    else
        print("failed to encode!")
    end
end


initDevice()

-- tcp server
if tcpS then
    tcpS:listen(8085, function(conn)
        conn:on("receive", function(c, data)
            tcpC = c
            print("receive: " .. data)
            if data == 'Reset' then
                node.restart()
            else  -- encode data to emit
                uart.write(0, data)
            end
        end)
        conn:on("disconnection", function(c, d) 
            print("disconnect")
            tcpC = nil
        end)
    end)
end


-- decode data to send
tmr.alarm(0, 500, tmr.ALARM_SINGLE, function()
    uart.on("data", 14, function(data)
        if tcpC ~= nil then
            tcpC:send(data)
        end
    end)
end)
