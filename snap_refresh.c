#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>




void enter_to_continue() {
    printf("Press Enter to continue...\n");
    while (getchar() != '\n') {}
}

void exec_snap_refresh() {
  const char *path="/usr/bin/snap";
  const char *arg1="refresh";

  printf("Refreshing snaps...\n");
  execlp(path, path, arg1, (char *) NULL);
}


int fork_then(void (*child)(), void (*parent)()) {
  if (fork()) {
    int wstatus;
    wait(&wstatus);
    parent();
    return wstatus;
  } else {
    child();
  }
}
  
int main() {

  int wstatus = fork_then(exec_snap_refresh, enter_to_continue);
  return wstatus;
}
