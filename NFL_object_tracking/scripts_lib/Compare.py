import sys,json,math
import difflib
from collections import OrderedDict

TIME = 0
DT = 1
STAT = 2
STAT_STR = 3

TRANSIENT = 1.0
RANGE = 5.0
################################################################################
#
def filteredEvents(file,save=False):
    """
    create list of unique events from log file
    """
    print 'reading events from (%s)'%file
    events = list()
    outfile = None

    with open(file) as input:
        prv_status = None
        last = None
        lines = list()
        for line in (line.strip() for line in input):
            status = json.loads(line)
            cur_status = status.get('stacker')
            # identify when status changes
            if cur_status is not None and cur_status != prv_status:
                cur_time = float(status.get('time'))

                if last is not None:
                    dt = cur_time - last[TIME]
                    last[DT] = dt
                    # ignore transient events (less than 1 sec duration)
                    if dt < TRANSIENT:
                        #print 'removing %.3f %.3f %s'%(last[1],last[2],file)
                        # remove last index
                        events.remove(last)
                        lines = lines[:-1]

                # [time, dt, status, status string, file]
                last = [cur_time,-1,cur_status,-1,file]
                events.append(last)
                lines.append(line)
                prv_status = cur_status


        if save:
            # save filtered events using lines from original file
            prd = file.rfind('.')
            tmpfile = file[:prd] + '_filtered_events_lines' + file[prd:]
            print 'writing events to (%s)'%tmpfile
            with open(tmpfile,'w') as output:
                for line in lines:
                    output.write(line+'\n')

            # save filtered events without times
            prd = file.rfind('.')
            outfile = file[:prd] + '_filtered_events' + file[prd:]
            print 'writing events to (%s)'%outfile
            with open(outfile,'w') as output:
                for event in events:
                    status = event[STAT]
                    # output status without time
                    ss = json.dumps(status, sort_keys=True)
                    event[STAT_STR] = ss
                    output.write(ss +'\n')

    return events, outfile

################################################################################
#
def complexMatch(cur_log,tst_log,save):

    # create filtered event files without time (stacker status only)
    cur_event, cur_file = filteredEvents(cur_log,save)
    tst_event, tst_file = filteredEvents(tst_log,save)

    cur_file = cur_file if cur_file is not None else cur_log
    tst_file = tst_file if tst_file is not None else tst_log


    # create list of lines for diff
    cur_lines = list()
    tst_lines = list()

    for events, lines in [(cur_event, cur_lines), (tst_event, tst_lines)]:
        for event in events:
            ss = event[STAT_STR]
            # check that string exists
            if ss == -1:
                ss = json.dumps(event[STAT], sort_keys=True)
                event[STAT_STR] = ss
            lines.append(ss)                

    cur_max = len(cur_event)
    tst_max = len(tst_event)

    # compare events
    diffs = difflib.ndiff(cur_lines, tst_lines)
    cur_line = 0
    tst_line = 0
    matching = list()
    cur_unique = []
    tst_unique = []
    different = list()
    last = None
    for dif in diffs:
        if False:
            print '--------------------\n',dif[0:2],cur_line+1,tst_line+1
            cc = dif[0]

        if dif[0] == '-' or dif[0] == '+':
            # line exists in only one file
            last = (cur_line, tst_line)
            if dif[0] == '-':
                if cur_line < cur_max:
                    cur_unique.append(cur_line)
                cur_line += 1
            else:
                #print 'different tst',tst_line+1
                if tst_line < tst_max:
                    tst_unique.append(tst_line)
                tst_line += 1
        else:
            if cur_line < cur_max and tst_line < tst_max:
                if dif[0] == ' ':
                    # identical lines in both files
                    matching.append((cur_line,tst_line))
                    cur_line += 1
                    tst_line += 1
                else:
                    # lines are in both files but are different
                    # check if they are different
                    if last[0] < cur_max and last[1] < tst_max:
                        # confirm they are different
                        if cur_event[last[0]][STAT_STR] != tst_event[last[1]][STAT_STR]:
                            # line are only difference once
                            if last[0] not in [dd[0] for dd in different] and last[1] not in [dd[1] for dd in different]:
                                different.append(last)
                last = None

    # remove lines from unique if in different
    cur_dif = [dd[0] for dd in different]
    tmp = list()
    for line in cur_unique:
        if line not in cur_dif:
            tmp.append(line)
    cur_unique = [tt for tt in tmp]

    tst_dif = [dd[1] for dd in different]
    tmp = list()
    for line in tst_unique:
        if line not in tst_dif:
            tmp.append(line)
    tst_unique = [tt for tt in tmp]

    errors = list()

    try:
        # only concerned with tst events that weren't found
        unique = [(tst_event, tst_unique, tst_file)]
        for event, lines, file in unique:
            for line in lines:
                tt = event[line][TIME]

                # find next lines that are the matching
                lines = None
                for cl,tl in matching:
                    if event == cur_event:
                        if cl > line:
                            lines = (cl,None)
                            break
                    else:
                        if tl > line:
                            lines = (None,tl)
                            break

                if lines is not None:
                    if event == cur_event:
                        # get dt to matching lines
                        match_time = cur_event[lines[0]][TIME]
                        dt = match_time - tt
                    else:
                        match_time = tst_event[lines[1]][TIME]
                        dt = match_time - tt
                    # ignore if transitient difference (same in less than 2 seconds)
                    if dt < 2.0:
                        # ignore
                        continue

                dt = event[line][DT]
                ss = event[line][STAT_STR]
                errors.append('time %.3f dt %.3f line %d only in %s\n%s\n'%(tt,dt,line,file,ss))

        for cur_line, tst_line in different:
            # line exists in both files but has differences
            cur_dat = cur_event[cur_line]
            tst_dat = tst_event[tst_line]

            if True:
                # find next lines that are the matching
                lines = None
                for cl,tl in matching:
                    if cl > cur_line:
                        lines = (cl,tl)
                        break

                if lines is not None:
                    # get dt to matching lines
                    cur_time = cur_dat[TIME]
                    tst_time = tst_dat[TIME]
                    cur_line = lines[0]
                    tst_line = lines[1]
                    cur_match_time = cur_event[cur_line][TIME]
                    tst_match_time = tst_event[tst_line][TIME]
                    cur_dt = cur_match_time - cur_time
                    tst_dt = tst_match_time - tst_time
                    # ignore if transitient difference (same in less than 2 seconds)
                    if cur_dt < TRANSIENT*2 or tst_dt < TRANSIENT*2:
                        # ignore
                        continue

            cur_stackers = dict((ss.get('id'),ss.get('state')) for ss in cur_dat[STAT])
            tst_stackers = dict((ss.get('id'),ss.get('state')) for ss in tst_dat[STAT])

            for cur_id,cur_states in cur_stackers.iteritems():
                tst_states = tst_stackers.get(cur_id)

                if tst_states is not None:

                    cur_state = dict((ss.get('type'),ss.get('value')) for ss in cur_states)
                    tst_state = dict((ss.get('type'),ss.get('value')) for ss in tst_states)

                    err = str()

                    for cur_type, cur_val in cur_state.iteritems():
                        tst_val = tst_state.get(cur_type)
                        if cur_val != tst_val:
                            err += '     %s cur (%s) tst (%s)\n'%(cur_type,str(cur_val),str(tst_val))

                    if len(err) > 0:
                        errors.append('stacker %d time cur (%.3f) tst (%.3f)\n'%(cur_id,cur_dat[TIME],tst_dat[TIME]))
                        errors.append(err)

    except (KeyError, IndexError):
        print 'Index does not exist cur %d of %d tst %d of %d'%(cur_line,len(cur_event),tst_line,len(tst_event))

    if len(errors) > 0:
        for err in errors:
            print err
        raise ValueError
    else:
        print 'no errors found'

################################################################################
#
def simpleMatch(cur_log,tst_log,save):

    # create filtered event files without time (stacker status only)
    cur_event, cur_file = filteredEvents(cur_log,save)
    tst_event, tst_file = filteredEvents(tst_log,save)

    match = list()
    for tst_evt in tst_event:
        tst_time= tst_evt[TIME]
        tst_status = tst_evt[STAT]
        for cur_evt in cur_event:
            cur_time = cur_evt[TIME]
            dt = cur_time - tst_time
            # fuzzy test within 5 seconds
            if math.fabs(dt) < RANGE:
                cur_status = cur_evt[STAT]
                if tst_status == cur_status:
                    match.append(tst_evt)
                    break
    lmat = len(match)
    ltst = len(tst_event)
    if lmat == ltst:
        print 'logs match'
    else:
        dif = ltst - lmat
        print '%d events of %d do not match %d%% in %s'%(dif,ltst,100*dif/ltst,tst_log)
        for event in tst_event:
            if event not in match:
                print 'match not found for time %.3f'%event[TIME]
        raise ValueError

################################################################################
#
def compareLogs(curlog,tstlog,save):
    """
    compare current log to test log
    """
    print 'comparing (%s) (%s)'%(curlog,tstlog)
    
    simpleMatch(curlog,tstlog,save)

################################################################################
#
def main():

    global TRANSIENT, RANGE
    
    if len(sys.argv) < 3:
        print 'usage: Compare.py <new log> <baseline log>' 
        print 'options:'
        print '-s simple comparison (default)'
        print '   -r x.x time range for finding matching events (default 5.0 secs, simple comparison only)'
        print '-c complex comparison'
        print '-w write intermediate/temp files (default is not write)'
        print '-t x.x transient filter time (default 1.0 secs)'
        print ''
        return

    newlog = sys.argv[1]
    tstlog = sys.argv[2]

    save = False
    state = None
    compare = simpleMatch
    for arg in sys.argv[3:]:
        if state == None:
            if arg == '-c':
                compare = complexMatch
            elif arg == '-w':
                save = True
            elif arg == '-t':
                state = 'transient'
            elif arg == '-r':
                state = 'range'
            else:
                print 'unknown arg (%s)'%arg
        elif state == 'transient':
            TRANSIENT = float(arg)
            state = None
        elif state == 'range':
            RANGE = float(arg)
            state = None
        else:
            print 'unknown arg (%s)'%arg

    print 'args',sys.argv[1:]

    if compare == simpleMatch:
        print 'simple comparison: transient %.1f range %.1f save %s'%(TRANSIENT, RANGE, save)
    elif compare == complexMatch:
        print 'complex comparison: transient %.1f save %s'%(TRANSIENT,save)

    compare(newlog,tstlog,save)

if __name__ == '__main__':
    try:
        main()
        error = False
    except:
        error = True
    sys.exit(error)

