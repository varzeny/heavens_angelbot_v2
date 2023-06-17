import subprocess

result = subprocess.run(
    "nmcli device show wlo1 | grep IP4.ADDRESS",
    shell=True,
    capture_output=True,
    text=True
).stdout.split(" ")[-1].split("/")[0]


print( result )

