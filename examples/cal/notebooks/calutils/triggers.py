# Run external programs
import subprocess

# extract data from xml files
import glue.ligolw

def run_pycbc_inspiral(FRAME_FILE, channel_name, BANK_FILE, OUTPUT_FILE, PSD_OUTPUT_FILE, TRIG_START_TIME, DURATION, BUFFER):
    """
    Search for an inspiral event in the time interval [TRIG_START_TIME, TRIG_START_TIME+DURATION] 

    BUFFER: INT
        GPS_START_TIME will be BUFFER seconds befor TRIG_START_TIME.
    """
    # gps start and end times for recording triggers
    # !!!Why does this interval need to be less than the GPS times?!!!
    TRIG_END_TIME = TRIG_START_TIME + DURATION
    # gps start and end times of the data you want to look at
    GPS_START_TIME = TRIG_START_TIME - BUFFER
    GPS_END_TIME = TRIG_END_TIME + BUFFER
    
    ######## Do matched filtering with pycbc_inpsiral ########
    command = ('pycbc_inspiral --segment-end-pad 64 \
               --segment-length 256 \
               --segment-start-pad 64 \
               --psd-estimation median \
               --psd-segment-length 256 \
               --psd-segment-stride 128 \
               --psd-inverse-length 16 \
               --pad-data 8 \
               --sample-rate 4096 \
               --low-frequency-cutoff 40 \
               --strain-high-pass 30 \
               --filter-inj-only  \
               --processing-scheme cpu \
               --cluster-method window \
               --cluster-window 10 \
               --approximant SPAtmplt \
               --order 7 \
               --snr-threshold 5.5 \
               --channel-name '+channel_name+' \
               --gps-start-time '+str(GPS_START_TIME)+' \
               --gps-end-time '+str(GPS_END_TIME)+' \
               --trig-start-time '+str(TRIG_START_TIME)+' \
               --trig-end-time '+str(TRIG_END_TIME)+' \
               --output '+OUTPUT_FILE+' \
               --frame-files '+FRAME_FILE+' \
               --bank-file '+BANK_FILE+' \
               --psd-output '+PSD_OUTPUT_FILE+' \
               --user-tag PYCBC \
               --zpk-z 100. 100. 100. 100. 100. \
               --zpk-p 1. 1. 1. 1. 1. \
               --zpk-k 1e-10 \
               --normalize-strain 3995. \
               --verbose')
    
    proc = subprocess.Popen(command, shell=True)
    proc.wait()


def get_trigger_corresponding_to_injection(trigger_xml_file, inj_time, dt):
    """
    Load a .xml file that contains a list of the triggers.
    Return the first trigger found in the interval [inj_time-dt, inj_time+dt].
    """
    
    # Create content handler (?)
    class DefaultContentHandler(glue.ligolw.lsctables.ligolw.LIGOLWContentHandler):
        pass
    glue.ligolw.lsctables.use_in(DefaultContentHandler)
    
    # Load xml document containing properties for all the triggers
    inspiral_xml = glue.ligolw.utils.load_filename(trigger_xml_file, contenthandler=DefaultContentHandler)
    
    # Get a list of sngl_inspiral trigger events from the inspiral_xml file object
    sngl_table = glue.ligolw.table.get_table(inspiral_xml, glue.ligolw.lsctables.SnglInspiralTable.tableName)
    
    for row in sngl_table:
        # row.end_time is GPS time of coalesence in seconds
        # row.end_time_ns is the decimal in ns
        tc = row.end_time+1.0e-9*row.end_time_ns

        # If you find the injection, exit the for loop
        if tc>inj_time-dt and tc<inj_time+dt:
            return tc, row
    
    # You made it out of the for loop, so no trigger corresponds to the time of the injected event
    raise Exception, 'Trigger corresponding to inj_time ='+str(inj_time)+' +/- '+str(dt)+' not found in .xml file.'

