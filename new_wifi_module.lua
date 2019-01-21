station_cfg={}
station_cfg.ssid="HiWiFi_4C1756"
station_cfg.pwd="lsj666666"
station_cfg.save=false

wifi.setmode(wifi.STATION)
wifi.sta.config(station_cfg)
wifi.sta.autoconnect(1)

remote_server_ip = "192.168.199.171"
remote_server_port = 9090

function startServer()
    sv = net.createServer(net.TCP, 30)
    function receiver(sck, data)
        sck:close()
        if(data == "test") then
            sendData(remote_server_ip, remote_server_port, "hello from the other side")
        end
        changeDoorState(data)
    end
    if sv then
        sv:listen(8080, function(conn)
            conn:on("receive", receiver)
            conn:send("hello world")
        end)
    end
end

function sendData(ip_addr, port, data)
    srv = net.createConnection(net.TCP, 0)
    srv:on("receive", function(sck, c)
        changeDoorState(c)
    end)
    srv:on("connection", function(sck, c)
        sck:send(data)
    end)
    srv:connect(port,ip_addr)
end

function changeDoorState(response)
    if(response == "t") then
        uart.write(0, "t")
    elseif(response == "f") then
        uart.write(0, "f")
    else 
    end
end

tmr.alarm(1, 1000, 1, function() 
   if wifi.sta.getip() == nil then
   else
        tmr.stop(1)
        startServer()
   end
end)

function ledLight()
    ledPin = 4
    gpio.mode(ledPin,gpio.OUTPUT)
    gpio.write(ledPin, 0)
    tmr.delay(3000)
    gpio.write(ledPin, 1)
end

uart.on("data", 8,
  function(data)
    if data == "quitquit" then
        ledLight()
        uart.on("data")
    else
        sendData(remote_server_ip, remote_server_port, data)
    end
end, 0)

