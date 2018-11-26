import facebook

graph = facebook.GraphAPI(access_token="EAAHmhSZBZAB3IBAJcxOZAITDJSEKOOSEerUnXihp4obU73K"
                                       "oCwHyDLVYwdgBF2ZCWUUZAgtQqoO0P6BWGgSQY2JZCmZCT61"
                                       "xu1qAmdhPm2stE0ogddhaj7U8rJd33rKyZBDfew4CZBcRjII"
                                       "HdzIeqjq4qI3fStZB8hs28zyQJ7FPgaVr2Cx7QDgu4t6p1wo"
                                       "USkpZBIZD", version="2.12")
my_friends = graph.get_connections(id="1925456114174926", connection_name="friends")
print (my_friends)