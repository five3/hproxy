import os
import sys
import importlib
import argparse
import urllib.parse

from werkzeug.routing import BaseConverter
from flask import Flask, request
from requests import request as sender

from .plugins import pre_proxy, post_proxy


__all__ = ['main']


class METHOD:
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'


class Action:
    @staticmethod
    def warp_request_data(payload):
        """
        :param payload: {
            'path': path,
            'url': url,
            'method': method,
            'headers': dict(headers),
            'query': query,
            'form_data': form_data,
            'body': body.decode('utf-8'),
            'files': files
        }
        :return:
        """
        send_data = {'method': payload['method'], 'url': payload['url'],
                     'headers': payload['headers'], 'data': None, 'files': None}

        if payload['method'] in (METHOD.GET, METHOD.HEAD, METHOD.OPTIONS):
            send_data['data'] = payload['query']
        elif payload['method'] in (METHOD.POST, METHOD.DELETE, METHOD.PUT):
            if payload['query']:
                payload['url'] = f"{payload['url']}?{urllib.parse.urlencode(payload['query'])}"
            if payload['form_data']:
                ct = payload['headers'].get('Content-Type')
                if 'application/x-www-form-urlencoded' in ct:
                    send_data['data'] = payload['form_data']
                elif 'multipart/form-data' in ct:
                    send_data['data'] = payload['form_data']
                    send_data['files'] = payload['files']
            elif payload['body']:
                send_data['data'] = payload['body']
            elif payload['files']:
                send_data['files'] = payload['files']

        return send_data

    @staticmethod
    def send_request(req):
        return sender(req['method'].lower(), req['url'], headers=req['headers'],
                      data=req['data'], files=req['files'])

    @staticmethod
    def warp_response_data(rep):
        body = rep.content
        if 'Transfer-Encoding' in rep.headers:      # 不支持chunk
            del rep.headers['Transfer-Encoding']
            rep.headers['Content-Length'] = len(body)
        if 'Connection' in rep.headers:             # 不支持keep-alive
            del rep.headers['Connection']
        if 'Content-Encoding' in rep.headers:       # 不支持gzip
            del rep.headers['Content-Encoding']
        rep.headers['Server'] = 'host proxy/0.1'    # 修改服务器信息

        return {
            'code': rep.status_code,
            'headers': dict(rep.headers),
            'body': body
        }


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.url = url_map
        self.regex = args[0]   # 正则的匹配规则

    def to_python(self, value):
        return value


app = Flask(__name__, static_url_path='/do_not_use_this_path__')
app.url_map.converters['re'] = RegexConverter


@app.route('/<re(r".*"):path>')
def proxy(path):
    url = request.base_url
    query = request.args
    method = request.method
    headers = request.headers
    form_data = request.form
    body = request.data.decode('utf-8')
    files = request.files

    payload = {
        'path': f'/{path}',
        'url': url,
        'method': method,
        'headers': dict(headers),
        'query': query,
        'form_data': form_data,
        'body': body,
        'files': files
    }

    context = {}
    req = Action.warp_request_data(payload)

    context['request'] = req
    pre_proxy.fire(context)

    rep = Action.send_request(req)
    ret = Action.warp_response_data(rep)

    context['response'] = ret
    post_proxy.fire(context)

    return ret['body'], ret['code'], ret['headers']


def main():
    parser = argparse.ArgumentParser(description="host proxy")
    parser.add_argument('--script', '-s', required=False, default='script.py', type=str,
                        action='store', help='plugin script')
    args = parser.parse_args()

    if args.script:
        if not os.path.exists(args.script):
            print(f'The Script {args.script} Not Exist!')
            parser.print_help()
            exit(1)

        abs_path = os.path.abspath(args.script.strip())
        path_dir = os.path.dirname(abs_path)
        if path_dir not in sys.path:
            sys.path.insert(0, path_dir)

        module = os.path.basename(abs_path)
        if module.endswith('.py'):
            module = module[:-3]
        _plugin_script_ = importlib.import_module(module)
        #:TODO: add filter

    app.run(host='0.0.0.0', port=80)
