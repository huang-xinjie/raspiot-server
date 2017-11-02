-- switch.lua
station_config = {}
station_config.ssid = "raspiot_0x0001"
station_config.pwd = "rasp_Iot"

print('Setting up WIFI...')
wifi.setmode(wifi.STATION)
wifi.sta.config(station_config)
wifi.sta.connect()

tcpS = net.createServer(net.TCP, 10)
pin = 3
switchStatus = 'false'
gpio.mode(pin, gpio.OUTPUT)

function getStatus()
    return switchStatus
end

function switch(command)
    if command == "true" then
        gpio.write(pin, gpio.HIGH)
        switchStatus = 'true'
    else
        gpio.write(pin, gpio.LOW)
        switchStatus = 'false'
    end
    return switchStatus
end

function sayHelloToManager(times)
    if times == 0 then
        return false
    end
    json = buildJSON(wifi.sta.getip(), wifi.sta.getmac())
    srv = net.createConnection(net.TCP, 0)
    srv:connect(22015, "192.168.17.1")
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

function buildJSON(ip, uuid)
    msgtable = {}
    msgtable.ip = ip
    msgtable.uuid = uuid
    msgtable.device = "smart fan"
    msgtable.identity = "device"
    msgtable.repository = "raspIot"
    msgtable.iotServer = "SmartFan"
    
    ok, json = pcall(sjson.encode, msgtable)
    if ok then
        print(json)
        return json
    else
        print("failed to encode!")
    end
end

tmr.alarm(1, 1000, tmr.ALARM_AUTO, function()
    if wifi.sta.getip() == nil then
        print('Waiting for IP ...')
    else
        print('IP is ' .. wifi.sta.getip())
        times = 3
        sayHelloToManager(times)
        tmr.stop(1)
    end
end)

if tcpS then
    tcpS:listen(8085, function(conn)
        conn:on("receive", function(c, data)
            print(data)
            if data == 'Reset' then
                node.restart()
            elseif data == 'getStatus' then
                c:send(getStatus())
            else
                c:send(switch(data))
            end
        end)
        conn:on("disconnection", function(c, d) print("disconnect") end)
    end)
end
