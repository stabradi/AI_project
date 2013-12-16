set ns [new Simulator]

$ns color 1 Blue
$ns color 2 Red

# Set up trace
set trc [open out.trc w]
set namtrc [open out.nam w]
$ns trace-all $trc
$ns namtrace-all $namtrc

proc finish {} {
	global ns trc
	global ns namtrc
	$ns flush-trace
	close $trc
	close $namtrc
	exec nam out.nam &
	exit 0
}

# Simulation parameters
set n 5
set bw 150000000; #150 Mb/s

# Set up bottleneck link
set gw  [$ns node]
set rgw [$ns node]
$ns duplex-link $gw $rgw $bw .30 DropTail

set snd {}; # TCP senders sitting on the gateway node
set trf {}; # Traffic generators for the senders
set dst {}; # Destination nodes hosting the receivers
set rcv {}; # TCP receivers sitting on the destination

for {set i 0} {$i<$n} {incr i} {
	# Create the objects needed for a new connection
	lappend snd [new Agent/TCP]
	lappend rcv [new Agent/TCPSink]
	lappend trf [new Application/Traffic/Pareto]	
	lappend srv [$ns node]

	# set up source and destination nodes
	$ns attach-agent $gw [lindex $snd $i]
	$ns attach-agent [lindex $srv $i] [lindex $rcv $i]
	[lindex $trf $i] attach-agent [lindex $snd $i]

	# Connect nodes
	$ns duplex-link $rgw [lindex $srv $i] 1000000000000 .100 DropTail
	# Connect agents
	$ns connect [lindex $snd $i] [lindex $rcv $i]
}

foreach traffic $trf {
	$ns at 0.0 "$traffic start"
}
$ns at 10.0 "finish"

$ns run
