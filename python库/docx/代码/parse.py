#!/usr/bin/python
import json
import unittest
import xmlrunner
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS


def setUpModule():
    'called once, before anything else in this module'
    pass


def tearDownModule():
    'called once, after everything else in this module'
    pass


def parse(parse_path):
    'TODO: return pass tree of a question by call rest service of search engine.'
    parse=[]
    with open(parse_path, 'r') as parse_file:
        for row in parse_file:
            parse.append(row.rstrip('\n'))
    return parse


def load_question(question_path):
    'TODO: load question from local file.'
    que = []
    with open(question_path, 'r') as question_file:
        for question in question_file:
            que.append(question.rstrip('\n'))
    return que


def load_parse_tree(parse_tree_path):
    'TODO: load parse tree from local file.'
    parse_tree=[]
    with open(parse_tree_path, 'r') as parse_tree_file:
        for row in parse_tree_file:
            parse_tree.append(row.rstrip('\n'))
    return parse_tree


model_source = ''
question_list = []
question_result_directory = ''


class SearchClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def send_question(self):
        if len(question_list) > 0:
            question = question_list.pop(0)
            cmd = {u'type': u'search', u'datas': {u'debug': True, u'position': len(question), u'search': question}}
            print 'sendMessage: ' + json.dumps(cmd) + '\n'
            self.sendMessage(json.dumps(cmd))
        else:
            pass
            # self.sendClose()
            reactor.stop()

    def save_result(self, message):
        if message[u'type'] == u'fatal':
            f = file(question_result_directory + 'parse.json', 'a+')
            new = '' + '\n'
            f.write(new)
            f.close()
            f = file(question_result_directory + 'insts.json', 'a+')
            new = '' + '\n'
            f.write(new)
            f.close()
            f = file(question_result_directory + 'insts_hum.json', 'a+')
            new = '' + '\n'
            f.write(new)
            f.close()
            f = file(question_result_directory + 'status.json', 'a+')
            new = 'timeout' + '\n'
            f.write(new)
            f.close()
            f = file(question_result_directory + 'annotations.json', 'a+')
            new = '' + '\n'
            f.write(new)
            f.close()

        elif message[u'type'] == u'test':
            f = file(question_result_directory + 'parse.json', 'a+')
            new = message[u'datas'][u'parse'] + '\n'
            f.write(new)
            f.close()
            if message[u'datas'].has_key(u'insts'):
                f = file(question_result_directory + 'insts.json', 'a+')
                #new = message[u'datas'][u'insts'] + '\n'
                new = json.dumps(json.loads(message[u'datas'][u'insts']),indent=2)+'\n'*2
                f.write(new)
                f.close()
            else:
                f = file(question_result_directory + 'insts.json', 'a+')
                new = '' + '\n'
                f.write(new)
                f.close()
            if message[u'datas'].has_key(u'insts_hum'):
                f = file(question_result_directory + 'insts_hum.json', 'a+')
                new = message[u'datas'][u'insts_hum'] + '\n'
                f.write(new)
                f.close()
            else:
                f = file(question_result_directory + 'insts_hum.json', 'a+')
                new = '' + '\n'
                f.write(new)
                f.close()
            if message[u'datas'].has_key(u'annotations'):
                f = file(question_result_directory + 'annotations.json', 'a+')
                new=str(json.dumps(message[u'datas'][u'annotations']))+'\n'
                #new = str(message[u'datas'][u'annotations']) + '\n'
                #new = json.dumps(json.loads(json.dumps(message[u'datas'][u'annotations'])),indent=2) + '\n'*2
                f.write(new)
                f.close()
            else:
                f = file(question_result_directory + 'annotations.json', 'a+')
                new = '' + '\n'
                f.write(new)
                f.close()

        elif message[u'type'] == u'state'and message[u'datas'] == u'searchFinished':
            f = file(question_result_directory + 'status.json', 'a+')
            new = 'searchFinished' + '\n'
            f.write(new)
            f.close()

    def onOpen(self):
        print 'send init: ' + model_source
        self.sendMessage(model_source)
        print 'ready to send the first question'
        self.send_question()

    def onMessage(self, msg, binary):
        print 'onMessage: ' + msg + '\n'
        result = json.loads(msg)
        self.save_result(result)

        if result[u'type'] == u'state' and result[u'datas'] == u'searchFinished':
            print 'recvOK,ready to send the next question'
            self.send_question()
        elif result[u'type'] == u'fatal':
            print 'Timeout,ready to send the next question'
            self.send_question()


def build_parse_tree_from_questions(questions_path, source_path, result_directory):
    "TODO: build parse tree file by questions in questions_path"
    global question_list, model_source, question_result_directory
    question_list = []
    with open(questions_path, 'r') as question_file:
        for question in question_file:
            question_list.append(question.rstrip('\n'))
    model_source = file(source_path, 'r').read()
    question_result_directory = result_directory
    factory = WebSocketClientFactory("ws://192.168.0.91:8101/websocket/search")
    factory.protocol = SearchClientProtocol
    connectWS(factory)
    reactor.run()

class ParserTest(unittest.TestCase):
    questions = load_question('data/base_questions_v1.6/questions_20170324.csv')
    que_id=range(len(questions))
    def setUp(self):
        self.questions = load_question('data/base_questions_v1.6/questions_20170324.csv')
        self.parse_trees = load_parse_tree('data/base_questions_v1.6/parse_tree.json')
        self.source = parse('data/base_questions_v1.6/result/parse.json')
    for i in range(len(questions)):
        formual_text = "def test_{f_name}(self): self.assertEqual(self.source[{f_id}], self.parse_trees[{f_id}],'{question}')"
        exec(formual_text.format(f_name=que_id[i],question=questions[i],f_id=i))
    def tearDown(self):
        pass

def save_test_result(save_test_path):#new
    suite=unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ParserTest))
    #runner=unittest.TextTestRunner(verbosity=2)
    runner = xmlrunner.XMLTestRunner(output=save_test_path)
    runner.run(suite)


build_parse_tree_from_questions('data/base_questions_v1.6/questions_20170324.csv', 'data/base_questions_v1.6/init.json', 'data/base_questions_v1.6/result/')
save_test_result('data/base_questions_v1.6/result/ParseTextReport.xml')






