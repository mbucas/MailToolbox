# MailToolbox

I've needed many times to move some of my emails to another place, and it's been a hard time every time.

Searching on the Web, I found many small tools in Python that can read emails from only one source storage
and write to only one email storage.

So I've decided to build a tool that can move emails from any source to any target. I want to make it easy to use with a nice interface with PyQt.

## When to use MailToolboxStudio

MailToolboxStudio will be handy in the following situations :

 - You are changing ISP and want to move your mail from the old ISP's IMAP server to the new one
 - You have multiple mail storages and want to centralize it in a single storage, either locally or in the cloud
 - You want to split your mail into folders based on mail sender, date or other categories (TODO)
 - You want to extract attachments from mails (TODO)
 - You want to extract mail informations as lists : mail addresses, dates, subjects, size (TODO)
 - Your company forces you to use a mail reader, and you want to use another one (MailToolboxStudio will not help you in sending mail)
 - You want to backup all you mails

## What MailToolboxStudio can't do

MailToolboxStudio is not designed to :

 - Synchronize 2 or more mail storages
 - View mail
 - Send or receive mail

## Current status

MailToolboxStudio currently can :
 - Read mail from Lotus Notes on Windows (the initial need I had)
 - Read mail from Outlook PST files on Windows
 - Read and write from Maildir, Mbox and Thunderbird mail storages, using standard Python library
 - Read and write from IMAP servers, also with SSL/TLS
  - For GMail IMAP access you have to enable IMAP and create an *application password*
 - Edit, save and load projects (passwords are saved in clear text)
 - Some mail transformations are working, but need some more testing

MailToolBoxRunner can run a project in the background.

## Next steps

I intend to work in order on :
 - Making more mail transformations work
 - Outlook PST files write
