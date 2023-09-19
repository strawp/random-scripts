import subprocess, os, shutil, base64, re

def shell():
  while True:
    try:
      cmd = input(os.getcwd() + "> ").strip()
      out = parse_command( cmd )
      print( out )
    except Exception as e:
      print("FAILED:",cmd, e)
      out = str(e)
    log( cmd, out )

def log( command, output ):
  if not output: output = ''
  with open(os.path.join(os.path.dirname(__file__),'shell.log'),'a') as f:
    f.write('\nCWD: '+os.getcwd()+'\nIN: '+command+'\nOUT: '+output)

def parse_command( cmd ):
  parts = cmd.split(' ')
  if len( parts ) == 0:
    print('huh?')
    return

  command = parts[0]
  if command == 'cd':
    out = do_cd( parts )
  elif command == 'ls':
    out = do_ls( parts )
  elif command == 'cat':
    out = do_cat( parts )
  elif command == 'bat':
    out = do_bat( parts )
  elif command == 'cp':
    out = do_cp( parts )
  elif command == 'mv':
    out = do_mv( parts )
  elif command == 'rm':
    out = do_rm( parts )
  elif command == 'exec':
    out = do_exec( parts )
  elif command == 'edit':
    out = do_exec( parts )
  elif command == 'grep':
    out = do_grep( parts )
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

def do_cd( parts ):
  if len( parts ) < 2:
    os.chdir(os.path.dirname(__file__))
  else:
    os.chdir(' '.join(parts[1:]))

def do_ls( parts ):
  d = resolve_path( parts )
  rtn = ''
  for f in os.listdir( d ):
    if os.path.isfile( f ):
      rtn += '\n' + str(os.path.getsize( f )).rjust(10) + ' ' + f
    else:
      rtn += '\n' + 'd'.rjust(10) + ' ' + f
  return rtn

def do_cat( parts ):
  d = resolve_path( parts )
  with open( d, 'r' ) as f:
    return f.read()

def do_bat( parts ):
  d = resolve_path( parts )
  with open( d, 'r' ) as f:
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
  return subprocess.run(f,shell=True, capture_output=True)

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

shell()
