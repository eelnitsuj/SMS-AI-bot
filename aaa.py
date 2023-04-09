import re

body_plain = 'Hi. I have gout and cancer and disease!!\r\n\r\nOn Sat, Apr 8, 2023 at 3:01\u202fAM Justin Lee <justin@superbonsai.com> wrote:\r\n\r\n> Hi. I have gout and cancer. Do you know how to fix it?\r\n>\r\n> On Sat, Apr 8, 2023 at 2:55\u202fAM Justin Lee <justin@superbonsai.com> wrote:\r\n>\r\n>> Hi. I have gout. Do you know how to fix it?\r\n>>\r\n>> On Sat, Apr 8, 2023 at 2:52\u202fAM Justin Lee <justin@superbonsai.com> wrote:\r\n>>\r\n>>> Hey there. What should i do about gout? it hurts a lot and i dont like it\r\n>>>\r\n>>> On Sat, Apr 8, 2023 at 2:45\u202fAM Justin Lee <justin@superbonsai.com>\r\n>>> wrote:\r\n>>>\r\n>>>> Hey there. What should i do about gout? it hurts a lot\r\n>>>>\r\n>>>> On Sat, Apr 8, 2023 at 2:44\u202fAM Justin Lee <justin@superbonsai.com>\r\n>>>> wrote:\r\n>>>>\r\n>>>>> Hey there. What should i do about gout? it hurts a lot\r\n>>>>>\r\n>>>>> On Sat, Apr 8, 2023 at 2:36\u202fAM Justin Lee <justin@superbonsai.com>\r\n>>>>> wrote:\r\n>>>>>\r\n>>>>>> Hey there. What should i do about gout?\r\n>>>>>>\r\n>>>>>> On Sat, Apr 8, 2023 at 2:30\u202fAM Justin Lee <justin@superbonsai.com>\r\n>>>>>> wrote:\r\n>>>>>>\r\n>>>>>>> OAIJFOAJDSOFJDSOIFJIODSFSF!@$@$!@$!@$\r\n>>>>>>>\r\n>>>>>>> On Fri, Apr 7, 2023 at 1:13\u202fPM Justin Lee <justin@superbonsai.com>\r\n>>>>>>> wrote:\r\n>>>>>>>\r\n>>>>>>>> please work!\r\n>>>>>>>>\r\n>>>>>>>> On Fri, Apr 7, 2023 at 3:07\u202fAM Justin Lee <justin@superbonsai.com>\r\n>>>>>>>> wrote:\r\n>>>>>>>>\r\n>>>>>>>>> hello!\r\n>>>>>>>>>\r\n>>>>>>>>\r\n'
text= "Hi. I have gout and cancer and disease!!\r\n\r\nOn Sat, Apr 8, 2023 at 3:01\u202fAM Justin Lee <justin@superbonsai.com> wrote:\r\n\r\n> Hi. I have gout and cancer. Do you know how to fix it?\r\n>\r\n> On Sat, Apr 8, 2023 at 2:55\u202fAM Justin Lee <justin@superbonsai.com> wrote:\r\n>\r\n>> Hi. I have gout. Do you know how to fix it?"

def remove_text_between_on_and_wrote(input_string):
    pattern = r'(?s)On .+?wrote:'
    modified_string = re.sub(pattern, '', input_string)
    while re.search(pattern, modified_string):
        modified_string = re.sub(pattern, '', modified_string)
    return modified_string

result = remove_text_between_on_and_wrote(body_plain)
print(result)