#include "key.h"
#include "serial.h"

#define STATE_INPUTTING 0
#define STATE_VALIAD 1
#define STATE_INVALIAD 2
#define STATE_DOOR_OPEN 3
#define STATE_ALERTING 4

// 轮询开门状态的间隔, 单位(ms)
#define POLL_INTERVAL 10000

// 门没有关闭的报警
#define ALERT_INTERVAL 5000

// keycode 和 键盘按键之间的对应
// 27 => A, 28 => B, 29 => C, 30 => D
#define CLOSE_DOOR_KEY_CODE 30 
#define OPEN_DOOR_KEY_CODE 29
#define REINPUT_KEY_CODE 28
#define INPUT_CONFIRM_KEY_CODE 27

u8 curPos = 0;
u8 first_time = 1;
u8 info_true[8] = {26, 26, 26, 26, 26, 26, 26, 26};
u8 info_false[8] = {15, 15, 15, 15, 15, 15, 15, 15};
u8 state = 0;
u8 password[8];

// RTC related
// u8	hour,minute,second;	//RTC变量
// u8 rtc[8];

// 记录门打开的时间
u8 door_open_time = 0;

void reset_led(){
    u8 i;
    for(i=0;i<8;i++){
        LED8[i] = DIS_;
    }
}

// void updateRTC(){
    
//     if(hour >= 10) {
//         rtc[0] = hour / 10;	
//     } else {
//         rtc[0] = DIS_BLACK;
//     }
// 	rtc[1] = hour % 10;
// 	rtc[2] = DIS_;
// 	rtc[3] = minute / 10;
// 	rtc[4] = minute % 10;
// 	rtc[5] = DIS_;
// 	rtc[6] = second / 10;
// 	rtc[7] = second % 10;
// }

void DisplayInfo(u8* info) {
    u8 i;
    for(i = 0; i < 8; i++) {
        LED8[i] = info[i];
    }

}

void initPassword(){
    u8 i;
    curPos = 0;
    for(i = 0; i < 8; i++) {
        password[i] = DIS_;
    }
    password[8] = 0;
}

void alert() {
    // 点亮LED
    P47 = 0;
    P46 = 0;
    // 发送报警信息到服务器
    PrintString1("aaaaaaaa");
}

void openDoorWithoutAlert() {
    // 取消报警, 进入正常的看门状态显示
    P47 = 1;
    P46 = 0;
    state = STATE_DOOR_OPEN;
}

void pollState() {
    if(state == STATE_DOOR_OPEN) {
        PrintString1("oooooooo");
    } else {
        PrintString1("cccccccc");       
    }
}

void cloesDoor() {
    // 关门，所有 led 灯关闭
    P47 = 1;
    P46 = 1;
    state = STATE_INPUTTING;
    initPassword();
}


void main(void) {

    u8 remoteKeyCode = 0;
    serial_init();
    key_init();
	initPassword();
    state = STATE_INPUTTING;
    // openDoorWithoutAlert();
    while(1)
    {
        // 检测是否收到数据
        if((TX1_Cnt != RX1_Cnt) && (!B_TX1_Busy))
        {
            // 收到数据，并将数据中的键码赋给变量remoteKeyCode
            remoteKeyCode = RX1_Buffer[TX1_Cnt];
            if(++TX1_Cnt >= UART1_BUF_LENGTH)   TX1_Cnt = 0;
        }

        // 受时间控制的功能
        if(B_1ms)
        {
            B_1ms = 0;

            // 记录当前门锁的状态，发送到服务器
            if(msecond >= POLL_INTERVAL) {
                msecond = 0;
                pollState();
            }

            if(state == STATE_DOOR_OPEN && msecond % ALERT_INTERVAL == 0) {
                if(door_open_time > 5) {
                    door_open_time = 0;
                    alert();
                }
                door_open_time ++;
            }

            if(++msecond % 200 == 0)
            {
                // 根据状态显示特定的数码管
                switch(state) {
                    case STATE_INPUTTING:
                        // ReadRTC();
                        // DisplayRTC();
                        if(password[0] == DIS_) {
                            ReadRTC();
                            DisplayRTC();
                        } else {
                            DisplayInfo(password);
                        }
                        break;
                    case STATE_VALIAD:
                        DisplayInfo(info_true);
                        break;
                    case STATE_INVALIAD:
                        DisplayInfo(info_false);                
                        break;
                    default: break;
                }
            }

            
            if(++cnt50ms >= 50)
            {
                cnt50ms = 0;
                IO_KeyScan();
            }

            if(KeyCode != 0)
            {
                if(state == STATE_INPUTTING && KeyCode >= 17 &&  KeyCode <= 26)              
                {
                    password[curPos++] = KeyCode % 17;
                } else if(KeyCode == INPUT_CONFIRM_KEY_CODE) {
                    if(curPos == 8) {
						u8 i;
						u8 tmp[8];
						for(i = 0; i < 8; i++) {
							tmp[i] = password[i] + 48;							
						}
                       	PrintString1(tmp);
                    }
                } else if(state == STATE_INVALIAD && KeyCode == REINPUT_KEY_CODE) {
                    state = STATE_INPUTTING;
                    initPassword();
                } else if(state == STATE_DOOR_OPEN && KeyCode == CLOSE_DOOR_KEY_CODE) {
                    // 如果有报警则取消报警
                    cloesDoor();
                } else if(state == STATE_VALIAD && KeyCode == OPEN_DOOR_KEY_CODE) {
                    // 直接开门
                    openDoorWithoutAlert();
                }

                KeyCode = 0;
            }

            if(remoteKeyCode != 0) {

                if(remoteKeyCode == 't') {
                    state = STATE_VALIAD;
                } else if (remoteKeyCode == 'f') {
                    state = STATE_INVALIAD;                    
                } else if (remoteKeyCode == 'o') {
                    // 提供远程开门的服务
                    openDoorWithoutAlert();
                }

                remoteKeyCode = 0;
            }
        }
    }
}
