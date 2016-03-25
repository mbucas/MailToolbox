# MailToolbox

I've needed many times to move some of my emails to another place, and it's been a hard time every time.

Searching on the Web, I found many small tools in Python that can read or write emails to one or more email storages so I've decided to build a tool that can move emails from any source to any target. I will make easy to use with a nice interface with PyQt4.

## When to use MailToolboxStudio

MailToolboxStudio will be handy in the following situations :

 - You are changing ISP and want to move your mail from the old ISP's IMAP server to the new one
 - You have multiple mail storages and want to centralize it in a single storage, either locally or "in the cloud"
 - You want to extract attachments from mails
 - You want to split your mail into folders based on mail sender, date or other categories
 - You want to extract mail informations as lists : mail addresses, dates, subjects, size
 - Your company forces you to use a mail reader, and you want to use another one (MailToolboxStudio will not help you in sending mail) 

## When not to use MailToolboxStudio

MailToolboxStudio is not designed to :

 - Synchronize 2 or more mail storages
 - Backup mail, as it would read all mails from the source each time.
 - View mail
 - Send or receive mail

## Current status

MailToolboxStudio currently can :
 - Read mail from Lotus Notes (the initial need I had)
 - Read and write from Maildir, Mbox and Thunderbird mail storages, using standard Python library
 - Edit, save and load projects (passwords are saved in clear text)
 - Only 2 mail transformations are working, but not fully tested

## Next steps

I intend to work in order on :
 - IMAP access, read and write, including SSL/TLS
 - Outlook access, read and write (local program, not the public webmail)
 - Making more mail transformations work
