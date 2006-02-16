def js(req):
  req.send_response(200)
  req.send_header("Content-Type", "text/javascript; charset: UTF-8")
  req.send_header('Connection', 'close')
  req.end_headers()
  req.wfile.write("""/* XMLHTTP functions 0.1 */
/* For all the Railsers out there */
/* started by Peter Cooper (coops) */
/* extended by .... */
/* licence is simple, use however you want, but leave attribution to any authors    listed above, including yourself :-) */ 

function xmlHTTPRequest(url, method, data) {
  if (!method) method = "GET";
  if (!data) data = null;
  req = xmlHTTPRequestObject();
  req.open (method, url, false);
  req.send (data);
  return req.responseText;
}

function xmlHTTPAsyncRequest(url, method, data, callbackr) {
  if (!method) method = "GET";
  if (!data) data = null;
  req = xmlHTTPRequestObject();
  req.onreadystatechange = callbackr;
  req.open (method, url, true);
  req.send (data);
  return req
}

function xmlHTTPRequestObject() {
    var obj = false;
    var objectIDs = new Array(
        "Microsoft.XMLHTTP",
        "Msxml2.XMLHTTP",
        "MSXML2.XMLHTTP.3.0",
        "MSXML2.XMLHTTP.4.0"
    );
    var success = false;

    for (i=0; !success && i < objectIDs.length; i++) {
        try {
            obj = new ActiveXObject(objectIDs[i]);
            success = true;
        } catch (e) { obj = false; }
    }

    if (!obj)
        obj = new XMLHttpRequest();

    return obj;
}
""")
