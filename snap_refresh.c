#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>

void enter_to_continue() {
    printf("Press Enter to continue...\n");
    while (getchar() != '\n') {}
}

void snap_refresh() {
  const char *path="/usr/bin/snap";
  const char *arg1="refresh";

  printf("Refreshing snaps...\n");
  execlp(path, path, arg1, (char *) NULL);
}

void snap_store_kill() {
  const char *path="/usr/bin/pkill";
  const char *arg1="snap-store";

  printf("Closing snap-store...\n");
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

void second_fork() {
  fork_then(snap_refresh, enter_to_continue);
}

int main() {
  return fork_then(snap_store_kill, second_fork);
}
