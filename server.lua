station_cfg={}
station_cfg.ssid="HiWiFi_4C1756"
station_cfg.pwd="lsj666666"
station_cfg.save=false

wifi.setmode(wifi.STATION)
wifi.sta.config(station_cfg)
wifi.sta.autoconnect(1)

remote_server_ip = "192.168.199.171"
remote_server_port = 9090

-- create server
function startServer()
    sv = net.createServer(net.TCP, 30)
    function receiver(sck, data)
        print(data)
        sck:close()
        if(data == "test") then
            sendData(remote_server_ip, remote_server_port, "hello from the other side")
        end 
    end
    if sv then
        sv:listen(8080, function(conn)
            conn:on("receive", receiver)
            conn:send("hello world")
        end)
    end
end

-- send data
function sendData(ip_addr, port, data)
    srv = net.createConnection(net.TCP, 0)
    srv:on("receive", function(sck, c)
        changeDoorState(c)
    end)
    -- Wait for connection before sending.
    srv:on("connection", function(sck, c)
        sck:send(data)
    end)
    srv:connect(port,ip_addr)
end

function changeDoorState(response)
    if(response == "t") then
        -- open the door
        uart.write(0, "t")
    elseif(response == "f") then
        -- close the door
        uart.write(0, "f")
    else 
        print("invalid input from server " + response)
    end
end

tmr.alarm(1, 1000, 1, function() 
   if wifi.sta.getip() == nil then
        print("Connect AP, Waiting...") 
   else
        tmr.stop(1)
        startServer()
   end
end)

-- uart 
uart.on("data", 8,
  function(data)
    print("receive from uart:", data)
    if data == "quitquit" then
        ledLight()
        print("cancel listener")
        uart.on("data")
    else
        -- receive input password from the door, send data to server and wait for response 
        sendData(remote_server_ip, remote_server_port, data)
    end
end, 1)

function ledLight()
    ledpin = 4
    gpio.mode(ledPin,gpio.OUTPUT)
    gpio.write(ledPin, 0)
    tmr.delay(1000)
    gpio.write(ledPin, 1)
end

