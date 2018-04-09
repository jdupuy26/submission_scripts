#!/bin/bash
# This file is for use with dogwood

echo "Submitting jobs..."

# Mass range (in log10 M_sun) 
# ( only integer values allowed )
IMIN=5
IMAX=5
# No. of runs 
JMIN=0
JMAX=5

# Begin loop
for ((i=${IMIN}; i<=${IMAX};i+=1))
	do 
		# Make mass directory
		mkdir m1e${i}
		cd m1e$i
		# Create run directories
		for ((j=${JMIN}; j<=${JMAX};j+=1))
			do 
				mkdir run$j
				# copy stuff over
				cp ../athinput.cylbgsbu run$j/
				cp ../hvcrun.sh run$j/
				cp ../athena run$j/
				# Edit this to produce different irand
				irand=$(expr $((j+1)) \* -$i)
				# edit files directly to right mass and irand 
				sed -i "s/^irand.*/irand = ${irand}/" run$j/athinput.cylbgsbu
				sed -i "s/^mhvc.*/mhvc = 1e${i}/" run$j/athinput.cylbgsbu
				# Submit the job
				cd run$j 
				sbatch runhvc	
				cd ../
			done 	
		cd ../ 
	done

echo "Program complete." 

