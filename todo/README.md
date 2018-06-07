## Todo Command Suite

A ruby command suite using GLI and terminal-table gems to manage a todo list.

### Synopsis
```
NAME
    todo - A simple todo app with ability to add & list todos and mark them as done

SYNOPSIS
    todo [global options] command [command options] [arguments...]

VERSION
    0.0.1

GLOBAL OPTIONS
    -f, --filename=todo_file - Path to the todo file (default: /Users/hoomandb/todo.txt)
    --help                   - Show this message
    -v, --[no-]verbosity     - be verbose
    --version                - Display the program version

COMMANDS
    add      - Add a new task to our todo
    complete - Mark a task as complete
    help     - Shows a list of commands or help for one command
    list     - List tasks
    
```

### Sample Commands
```
?> bundle exec bin/todo add 'call Mike'

?> bundle exec bin/todo list
+----+-----------+----------------------------+---------------------------+
| id | name      | created                    | completed                 |
+----+-----------+----------------------------+---------------------------+
| 1  | pushing   |  2018-06-07 17:00:18 +1000 | 2018-06-07 17:00:49 +1000 |
| 2  | newtown   |  2018-06-07 17:00:29 +1000 | -                         |
| 3  | call Mike |  2018-06-07 17:18:37 +1000 | -                         |
+----+-----------+----------------------------+---------------------------+

?> bundle exec bin/todo complete 3

?> bundle exec bin/todo list
+----+-----------+----------------------------+---------------------------+
| id | name      | created                    | completed                 |
+----+-----------+----------------------------+---------------------------+
| 1  | pushing   |  2018-06-07 17:00:18 +1000 | 2018-06-07 17:00:49 +1000 |
| 2  | newtown   |  2018-06-07 17:00:29 +1000 | -                         |
| 3  | call Mike |  2018-06-07 17:18:37 +1000 | 2018-06-07 17:19:14 +1000 |
+----+-----------+----------------------------+---------------------------+
```

