import json
from twisted.protocols import basic

from cxctools.string import to_bytes, to_str
from cxctools.dict import remove_key


class JsonReceiver(basic.LineOnlyReceiver):
    def lineReceived(self, data):
        str_data = to_str(data)

        try:
            decode_data = json.loads(str_data)
        except json.JSONDecodeError:
            self.invalid_json_received(str_data)
        else:
            self.object_received(decode_data)

    def object_received(self, obj):
        """
        Override this for when obj is received.

        :param obj: The object which was received.
        :type obj: dict
        """
        print('Data received: {}'.format(obj))

        if 'command' not in obj:
            print('empty command!')
            return

        command = obj['command']

        params = remove_key(obj, 'command')

        self.receive_command(command, **params)

    def invalid_json_received(self, data):
        pass

    def send_object(self, obj=None, **kwargs):
        dic = {}
        if obj:
            dic.update(obj)
        if kwargs:
            dic.update(kwargs)
        str_data = json.dumps(dic)
        data = to_bytes(str_data)

        print('Data send to {0}:{1}\n'
              '\t{2}'.format(self.peer.host, self.peer.port, data))

        self.sendLine(data)
