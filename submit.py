#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import hashlib
import email.message
import email.encoders

import time
from collections import namedtuple

Metadata = namedtuple("Metadata", ['url', 'name', 'part_data'])
Part = namedtuple("Part", ['sid', 'input_file', 'source', 'name'])

def check_login(metadata, login, password):
    sid = 'B5DXTczU-dev'
    submission = '0'
    source = ''

    print '== Checking Login Credentials ... '
    (login, ch, state, ch_aux) = get_challenge(metadata.url, login, sid)
    if((not login) or (not ch) or (not state)):
        print '\n!! Error: %s\n' % login
        return
    ch_resp = challenge_response(login, password, ch)
    (result, string) = submit_solution(metadata.url, login, ch_resp, sid, submission, source, state, ch_aux)
    if string.strip() == 'password verified':
        print '== credentials verified'
    else :
        print '\n!! login failed'
        print '== %s' % string.strip()
        quit()


def load_meta_data():
    try:
        metadata_file = open('_metadata', 'r')
        
        url = metadata_file.readline().strip()
        name = metadata_file.readline().strip()
        part_count = int(metadata_file.readline().strip())
        part_data = []
        for i in range(0,part_count):
            line = metadata_file.readline().strip()
            line_parts = line.split(',')
            line_parts = [x.strip() for x in line_parts]
            assert(len(line_parts) == 4)
            part_data.append(Part(*line_parts))
            
        metadata_file.close()
    except Exception, e:
        print 'problem parsing assignment metadata file'
        print 'exception message:'
        print e
        quit()
    return Metadata(url, name, part_data)
    
    
def submit():
    metadata = load_meta_data()
    #print metadata
    
    print '==\n==',metadata.name,'Solution Submission \n=='

    (login, password) = login_prompt()
    if not login:
        print '!! Submission Cancelled'
        return
    
    print '\n== Connecting to Coursera ... '
    check_login(metadata, login, password)

    selected_parts = part_prompt(metadata.part_data)
    
    for part in selected_parts:
        (login, ch, state, ch_aux) = get_challenge(metadata.url, login, part.sid)
        if not login or not ch or not state:
            print '\n!! Error: %s\n' % login
            return
        submission = output(part)

        ch_resp = challenge_response(login, password, ch)
        (result, string) = submit_solution(metadata.url, login, ch_resp, part.sid, submission, get_source(part.source), state, ch_aux)

        print '== %s' % string.strip()


def login_prompt():
    """Prompt the user for login credentials. Returns a tuple (login, password)."""
    (login, password) = basic_prompt()
    return (login, password)


def basic_prompt():
    """Prompt the user for login credentials. Returns a tuple (login, password)."""
    login = raw_input('Login (Email address): ')
    password = raw_input('Submission Password (from the programming assignments page. This is NOT your own account\'s password): ')
    return (login, password)


def part_prompt(parts):
    print 'Hello! These are the assignment parts that you can submit:'
    for i, part in enumerate(parts):
        print str(i+1) + ') ' + part.name
    print '0) All'

    part_text = raw_input('Please enter which part(s) you want to submit (0-'+ str(len(parts)) + '): ')
    selected_parts = []

    for item in part_text.split(','):
        try:
            i = int(item) - 1
        except:
            print 'Skipping input "' + item + '".  It is not an integer.'
            continue
        if i >= len(parts):
            print 'Skipping input "' + item + '".  It is out of range (the maximum value is ' + str(len(parts)) + ').'
            continue
        if i < 0:
            selected_parts.extend(parts)
        else:
            selected_parts.append(parts[i])

    if len(selected_parts) <= 0:
        print 'No valid assignment parts identified.  Please try again. \n'
        return part_prompt(parts)
    else:
        return selected_parts


def get_challenge(c_url, email, sid):
    """Gets the challenge salt from the server. Returns (email,ch,state,ch_aux)."""

    url = challenge_url(c_url)
    values = {'email_address': email, 'assignment_part_sid': sid, 'response_encoding': 'delim'}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    text = response.read().strip()

    splits = text.split('|')
    if len(splits) != 9:
        print 'Badly formatted challenge response: %s' % text
        return None
    return (splits[2], splits[4], splits[6], splits[8])


def challenge_response(email, passwd, challenge):
    sha1 = hashlib.sha1()
    sha1.update(''.join([challenge, passwd])) 
    digest = sha1.hexdigest()
    strAnswer = ''
    for i in range(0, len(digest)):
        strAnswer = strAnswer + digest[i]
    return strAnswer


def challenge_url(url):
    """Returns the challenge url."""
    return 'https://class.coursera.org/' + url + '/assignment/challenge'


def submit_url(url):
    """Returns the submission url."""
    return 'https://class.coursera.org/' + url + '/assignment/submit'


def submit_solution(c_url, email_address, ch_resp, sid, output, source, state, ch_aux):
    """Submits a solution to the server. Returns (result, string)."""
    source_64_msg = email.message.Message()
    source_64_msg.set_payload(source)
    email.encoders.encode_base64(source_64_msg)

    output_64_msg = email.message.Message()
    output_64_msg.set_payload(output)
    email.encoders.encode_base64(output_64_msg)
    values = { 
        'assignment_part_sid': sid,
        'email_address': email_address,
        # 'submission' : output, \
        'submission': output_64_msg.get_payload(),
        # 'submission_aux' : source, \
        'submission_aux': source_64_msg.get_payload(),
        'challenge_response': ch_resp,
        'state': state,
        }
    url = submit_url(c_url)
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    string = response.read().strip()
    result = 0
    return (result, string)


def get_source(source_file):
    """Collects the source code (just for logging purposes)."""
    f = open(source_file,'r')
    src = f.read()
    f.close()
    return src


try:
    pkg = __import__('solver')
    if not hasattr(pkg, 'solve_it'):
        print 'the solve_it() function was not found in solver.py'
        quit()
    solve_it = pkg.solve_it
except ImportError:
    print 'solver.py was not found in the python path.'
    quit()


def load_input_data(fileLocation):
    inputDataFile = open(fileLocation, 'r')
    inputData = ''.join(inputDataFile.readlines())
    inputDataFile.close()
    return inputData

def output(part):
    """Use student code to compute the output for test cases."""

    solution = ''

    start = time.clock()
    try:
        solution = solve_it(load_input_data(part.input_file))
    except Exception, e:
        print 'the solve_it(input_data) method from solver.py raised an exception'
        print 'try testing it with python ./solver.py before running this submission script'
        print 'exception message:'
        print e
        print ''
        return 'Local Exception =('
    end = time.clock()

    if not isinstance(solution, str):
        print 'Warning: the submitted solution was not ASCII and will be converted.  Some information may be lost.'
        print 'Orginal: '
        print solution
        solution = solution.encode('ascii', 'ignore')

    print 'Submitting: '
    print solution

    return solution.strip() + '\n' + str(end - start)


submit()
