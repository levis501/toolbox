#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
  //const char *path="/usr/bin/echo";
  const char *path="/usr/bin/snap";
  const char *arg1="refresh";
  
  pid_t pid = fork();
  if (pid) {
    // parent
    int wstatus;
    wait(&wstatus);
    printf("Press Enter to continue...\n");
    while (getchar() != '\n') {}
    return wstatus;
  } else {
    //child
    printf("Refreshing snaps...\n");
    return execlp(path, path, arg1, (char *) NULL);
  }
}
