import asyncio

from temporalio import activity

EMAIL_SEND_SLEEP_SECONDS = 0.2

@activity.defn
# TODO Fill this in: 
# define the send_confirmation_email activity, which takes an email address as input and returns a string. 
# The activity should sleep for EMAIL_SEND_SLEEP_SECONDS to simulate sending the email, then return a string confirming the email was sent to the given address.