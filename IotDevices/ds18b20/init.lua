-- ds18b20_init.lua
station_config = {}
station_config.ssid = "ssid"
station_config.pwd = "password"

print('Setting up WIFI...')
wifi.setmode(wifi.STATION)
wifi.sta.config(station_config)
wifi.sta.connect()

tcpS = net.createServer(net.TCP, 10)
sconn = nil

function readout(temp)
    for addr, temp in pairs(temp) do
        sconn:send(temp .. '*C')
    end
    sconn = nil
end

function getTemp(c)
    pin = 3
    sconn = c
    t = require('ds18b20')
    t:read_temp(readout, pin)
end

function sayHelloToManager(json)
    srv = net.createConnection(net.TCP, 0)
    -- default manager port and ip
    srv:connect(22015, "192.168.17.1")
    srv:send(json)
    srv:on("receive", function(sck, c) 
        print(c) 
        recvJson = sjson.decode(c)
        if recvJson.response == 'Setup completed' then
            return true
        else 
            sayHelloToManager(json)
        end
    end)
end

function buildJSON(ip, mac)
    msgtable = {}
    msgtable.ip = ip
    msgtable.mac = mac
    msgtable.device = "ds18b20"
    msgtable.identity = "device"
    msgtable.repository = "raspIot"
    msgtable.iotServer = "DS18B20"
    
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
        json = buildJSON(wifi.sta.getip(), wifi.sta.getmac())
        sayHelloToManager(json)
        tmr.stop(1)
    end
end)

if tcpS then
    tcpS:listen(8085, function(conn)
        conn:on("receive", function(c, data)
            print(data)
            if data == 'getTemp' then
                getTemp(c)
            elseif data == 'Reset' then
                node.restart()
            end
        end)
        conn:on("disconnection", function(c, d) print("disconnect") end)
    end)
end
