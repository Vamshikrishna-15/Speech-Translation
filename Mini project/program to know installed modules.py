from subprocess import Popen, PIPE

# Run the pip list command and capture the output
process = Popen(['pip', 'list'], stdout=PIPE, stderr=PIPE)
stdout, stderr = process.communicate()

# Decode the output and split it into lines to extract package names
installed_packages = [line.split()[0] for line in stdout.decode('utf-8').split('\n')[2:-1]]

print(installed_packages)
