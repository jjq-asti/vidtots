All:
demux:
	demuxfs -o backend=filesrc -o filesrc=/tmp/channel_program.ts -o standard=ISDB -o big_writes /media/demux
umount:
	sudo umount /media/demux

clean:
	rm videos/*.ts videos/*.avi videos/*.mp2 videos/*.pes videos/*.m2v
