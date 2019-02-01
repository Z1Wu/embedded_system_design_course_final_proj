station_cfg={}
station_cfg.ssid="360WiFi-F98C41"
station_cfg.pwd="18927143019"
station_cfg.save=false

wifi.setmode(wifi.STATION)
wifi.sta.config(station_cfg)
wifi.sta.autoconnect(1)

remote_server_ip = "192.168.0.10"
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
        -- send data to remote door
        changeDoorState(data)
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
    -- need to stay
    srv:on("connection", function(sck, c)
        sck:send(data)
    end)
    srv:connect(port,ip_addr)
end

function changeDoorState(response)
    if(response == "t") then
        -- valid password
        uart.write(0, "t")
    elseif(response == "f") then
        -- invalid password
        uart.write(0, "f")
    elseif(response == "o") then
        -- open the door
        uart.write(0, "o")
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

function ledLight()
    ledPin = 4
    gpio.mode(ledPin,gpio.OUTPUT)
    gpio.write(ledPin, 0)
    tmr.delay(3000)
    gpio.write(ledPin, 1)
end

-- uart 
-- 增加鲁棒性, 最后一个参数应该设置成0, 避免从 uart 的输入进入到 esp8266 中的interpreter 中
-- 由于执行的顺序问题，这个函数应该放在最后面，不然串口写入的脚本无法进入到控制台被执行

uart.on("data", '*',
  function(data)
    if(string.len(data) ~= 9 ) then
        -- do nothing, 
        return
    end
    print("receive from uart:", data)
    data = string.sub(data, 0, 8)
    print(data)
    if data == "quitquit" then
        ledLight()
        print("cancel listener")
        uart.on("data")
    else
        -- receive input password from the door, send data to server and wait for response 
        sendData(remote_server_ip, remote_server_port, data)
    end
end, 0)


-- 旧版本，存在问题，无法应对杂音问题
-- uart.on("data", 8,
--   function(data)
--     print("receive from uart:", data)
--     if data == "quitquit" then
--         ledLight()
--         print("cancel listener")
--         uart.on("data")
--     else
--         -- receive input password from the door, send data to server and wait for response 
--         sendData(remote_server_ip, remote_server_port, data)
--     end
-- end, 0)

