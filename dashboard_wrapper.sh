#!/bin/bash

# a wrapper script that restricts the user to only the squeue or scancel commands.
# the command they try to execute (captured as $SSH_ORIGINAL_COMMAND) must start with
# "squeue " or "scancel " (notice the trailing space).

# You can cause this wrapper to be run by putting the following (wuthout the leading #)
# in ~/.ssh/authorized_keys on one of the rhinos:

# command="/path/to/dashboard_wrapper.sh",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ssh-rsa AA... slurmdashboard@fhcrc.org
# where 'AA...' represents a truncated key (minus the leading ssh-rsa and trailing email-like identifier).

# so now if you try to ssh to rhino (assuming you are using the private key that corresponds to the
# key referenced in the authorized_keys file above) with a command that does NOT start with
# 'squeue ' or 'scancel ', you'll get a message saying "too bad, you can't do that."
# Otherwise, the command will run as is.

if [[ $SSH_ORIGINAL_COMMAND == 'squeue '* ]]  ||  [[ $SSH_ORIGINAL_COMMAND == 'sinfo '* ]] ;
then
     $SSH_ORIGINAL_COMMAND
else
    echo "too bad, you can't do that!"
fi
