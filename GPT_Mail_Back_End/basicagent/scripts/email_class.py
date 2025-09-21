'''
Just a class to model the important aspects of an email
'''

class Email():
    def __init__(self, msg_id, thd_id, subject, sender, date, body):
        self.msg_id=msg_id
        self.thd_id=thd_id
        self.subject=subject
        self.sender=sender
        self.date=date
        self.body=body
    def list_of_params(self):
        return [self.msg_id, self.thd_id, self.subject, self.sender, self.date, self.body]
    def create_new(self, params):
        '''
        Creates a new Email object with specified params\n
        Params of the form\n
        {"param_name": param_val}\n
        If a param is not specified, it is taken from the host object'''
        param_names=["msg_id", "thd_id", "subject", "sender", "date", "body"]
        paramlist=self.list_of_params()
        new_params=[]
        for i in range(len(param_names)):
            param=param_names[i]
            if (param in params):
                new_params.append(params[param])
            else:
                new_params.append(paramlist[i])
        return Email(new_params[0], new_params[1], new_params[2], new_params[3], new_params[4], new_params[5])