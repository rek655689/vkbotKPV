import update_pages
import time
import traceback


seconds = time.time()
local_time = time.ctime(seconds)

try:
    update_pages.check_members()
    update_pages.add_to_page()
except Exception as e:
    with open('errors.txt', 'a') as f:
        f.write('\nPages: '+local_time+' '+str(e)+'\n'+traceback.print_exc())
