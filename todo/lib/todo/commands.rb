require 'gli'
require 'terminal-table'

module Todo
    class Commands
        def self.add_task(file, new_task)
            File.open(file, 'a') do |f|
                f.puts "#{new_task}, #{Time.now}"
            end
        end

        def self.list_tasks(file, format)
            File.open(file, 'r') do |f|
                counter = 1
                rows = []
                f.readlines.each do |line|
                    name,created,completed = line.chomp.split(/,/)
                    case format
                    when :csv
                        printf("%3d - %s\n", counter, name)
                        printf("     Created   : %s\n",created)
                        printf("     Completed : %s\n",completed) unless completed.nil? || completed.strip.empty?
                    when :tabular
                        row = []
                        row << counter
                        row << name
                        row << created
                        row << ((completed.nil? || completed.strip.empty?) ? '-' : completed)
                        rows << row

                    counter += 1
                    end
                end
                if format == :tabular
                    header = [:id, :name, :created, :completed]
                    table = Terminal::Table.new(rows: rows, headings: header)
                    puts table
                end
            end
        end

        def self.mark_complete(file, task_number)
            puts "task number: #{task_number}"
            File.open(file, 'r') do |f|
                File.open('todo.txt.new', 'w') do |tmp_file|
                    counter = 1
                    f.readlines.each do |line|
                        name,created,completed = line.chomp.split(',')
                        if task_number == counter
                            tmp_file.puts("#{name},#{created},#{Time.now}")
                        else
                            tmp_file.puts("#{name},#{created},#{completed}")
                        end
                        counter += 1
                    end
                end
            end
            `mv todo.txt.new #{file}`
        end
    end
end

