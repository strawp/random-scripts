#!/usr/bin/env python
# Convert a markdown file into HTML that looks like it was generated in the default Outlook style

import sys, pypandoc, re

htmlformat='html'
markdownformat='gfm+pipe_tables'
extra = ['--wrap=preserve']

infile = sys.argv[1]

md = open(infile,'r').read()

html = pypandoc.convert_text( md, format=markdownformat, to=htmlformat, extra_args=extra )

# Preserve single line breaks
html = re.sub(r'([^>])($)',r'\1<br>',html, flags=re.M)

# Add spacing paragraphs
html = html.replace('</p>','</p>\n<p>&nbsp;</p>')

# Add Outlook tags
html = html.replace(r'<p>', r'<p class="MsoNormal"><span style="font-family:&quot;Nirmala UI&quot;,sans-serif;color:black">').replace( r'</p>', r'</span></p>' )

# List items
html = html.replace('<li>','<li class="MsoNormal">')

# Add HTML header stuff
html = '''
<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns:m="http://schemas.microsoft.com/office/2004/12/omml" xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta name="Generator" content="Microsoft Word 15 (filtered medium)">
<!--[if !mso]><style>v\:* {behavior:url(#default#VML);}
o\:* {behavior:url(#default#VML);}
w\:* {behavior:url(#default#VML);}
.shape {behavior:url(#default#VML);}
</style><![endif]--><style><!--
/* Font Definitions */
@font-face
	{font-family:"Cambria Math";
	panose-1:2 4 5 3 5 4 6 3 2 4;}
@font-face
	{font-family:Calibri;
	panose-1:2 15 5 2 2 2 4 3 2 4;}
@font-face
	{font-family:Verdana;
	panose-1:2 11 6 4 3 5 4 4 2 4;}
@font-face
	{font-family:"Nirmala UI";
	panose-1:2 11 5 2 4 2 4 2 2 3;}
@font-face
	{font-family:"Segoe UI Emoji";
	panose-1:2 11 5 2 4 2 4 2 2 3;}
@font-face
	{font-family:remialcxesans;}
@font-face
	{font-family:Tahoma;
	panose-1:2 11 6 4 3 5 4 4 2 4;}
@font-face
	{font-family:"Trebuchet MS";
	panose-1:2 11 6 3 2 2 2 2 2 4;}
@font-face
	{font-family:Roboto;}
/* Style Definitions */
p.MsoNormal, li.MsoNormal, div.MsoNormal
	{margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
a:link, span.MsoHyperlink
	{mso-style-priority:99;
	color:#0563C1;
	text-decoration:underline;}
a:visited, span.MsoHyperlinkFollowed
	{mso-style-priority:99;
	color:purple;
	text-decoration:underline;}
p.msonormal0, li.msonormal0, div.msonormal0
	{mso-style-name:msonormal;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.style1, li.style1, div.style1
	{mso-style-name:style1;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:11.0pt;
	font-family:"Times New Roman",serif;}
p.xmsonormal, li.xmsonormal, div.xmsonormal
	{mso-style-name:x_msonormal;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xmsonormal0, li.xmsonormal0, div.xmsonormal0
	{mso-style-name:x_msonormal0;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xstyle1, li.xstyle1, div.xstyle1
	{mso-style-name:x_style1;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:11.0pt;
	font-family:"Times New Roman",serif;}
p.xxmsonormal, li.xxmsonormal, div.xxmsonormal
	{mso-style-name:x_xmsonormal;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxmsonormal0, li.xxmsonormal0, div.xxmsonormal0
	{mso-style-name:x_xmsonormal0;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxstyle1, li.xxstyle1, div.xxstyle1
	{mso-style-name:x_xstyle1;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:11.0pt;
	font-family:"Times New Roman",serif;}
p.xxxmsonormal, li.xxxmsonormal, div.xxxmsonormal
	{mso-style-name:x_xxmsonormal;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxmsonormal0, li.xxxmsonormal0, div.xxxmsonormal0
	{mso-style-name:x_xxmsonormal0;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxstyle1, li.xxxstyle1, div.xxxstyle1
	{mso-style-name:x_xxstyle1;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:11.0pt;
	font-family:"Times New Roman",serif;}
p.xxxxmsonormal, li.xxxxmsonormal, div.xxxxmsonormal
	{mso-style-name:x_xxxmsonormal;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxxmsonormal0, li.xxxxmsonormal0, div.xxxxmsonormal0
	{mso-style-name:x_xxxmsonormal0;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxxstyle1, li.xxxxstyle1, div.xxxxstyle1
	{mso-style-name:x_xxxstyle1;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:11.0pt;
	font-family:"Times New Roman",serif;}
p.xxxxxmsonormal, li.xxxxxmsonormal, div.xxxxxmsonormal
	{mso-style-name:x_xxxxmsonormal;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxxxmsonormal0, li.xxxxxmsonormal0, div.xxxxxmsonormal0
	{mso-style-name:x_xxxxmsonormal0;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxxxstyle1, li.xxxxxstyle1, div.xxxxxstyle1
	{mso-style-name:x_xxxxstyle1;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:11.0pt;
	font-family:"Times New Roman",serif;}
p.xxxxxxmsonormal, li.xxxxxxmsonormal, div.xxxxxxmsonormal
	{mso-style-name:x_xxxxxmsonormal;
	margin:0cm;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxxxxmsochpdefault, li.xxxxxxmsochpdefault, div.xxxxxxmsochpdefault
	{mso-style-name:x_xxxxxmsochpdefault;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:10.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxxxmsochpdefault, li.xxxxxmsochpdefault, div.xxxxxmsochpdefault
	{mso-style-name:x_xxxxmsochpdefault;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:10.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxxmsochpdefault, li.xxxxmsochpdefault, div.xxxxmsochpdefault
	{mso-style-name:x_xxxmsochpdefault;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:10.0pt;
	font-family:"Calibri",sans-serif;}
p.xxxmsochpdefault, li.xxxmsochpdefault, div.xxxmsochpdefault
	{mso-style-name:x_xxmsochpdefault;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:10.0pt;
	font-family:"Calibri",sans-serif;}
p.xxmsochpdefault, li.xxmsochpdefault, div.xxmsochpdefault
	{mso-style-name:x_xmsochpdefault;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:10.0pt;
	font-family:"Calibri",sans-serif;}
p.xmsochpdefault, li.xmsochpdefault, div.xmsochpdefault
	{mso-style-name:x_msochpdefault;
	mso-margin-top-alt:auto;
	margin-right:0cm;
	mso-margin-bottom-alt:auto;
	margin-left:0cm;
	font-size:10.0pt;
	font-family:"Calibri",sans-serif;}
span.xmsohyperlink
	{mso-style-name:x_msohyperlink;
	color:#0563C1;
	text-decoration:underline;}
span.xmsohyperlinkfollowed
	{mso-style-name:x_msohyperlinkfollowed;
	color:purple;
	text-decoration:underline;}
span.xxmsohyperlink
	{mso-style-name:x_xmsohyperlink;
	color:#0563C1;
	text-decoration:underline;}
span.xxmsohyperlinkfollowed
	{mso-style-name:x_xmsohyperlinkfollowed;
	color:purple;
	text-decoration:underline;}
span.xxxmsohyperlink
	{mso-style-name:x_xxmsohyperlink;
	color:#0563C1;
	text-decoration:underline;}
span.xxxmsohyperlinkfollowed
	{mso-style-name:x_xxmsohyperlinkfollowed;
	color:purple;
	text-decoration:underline;}
span.xxxxmsohyperlink
	{mso-style-name:x_xxxmsohyperlink;
	color:#0563C1;
	text-decoration:underline;}
span.xxxxmsohyperlinkfollowed
	{mso-style-name:x_xxxmsohyperlinkfollowed;
	color:purple;
	text-decoration:underline;}
span.xxxxxmsohyperlink
	{mso-style-name:x_xxxxmsohyperlink;
	color:#0563C1;
	text-decoration:underline;}
span.xxxxxmsohyperlinkfollowed
	{mso-style-name:x_xxxxmsohyperlinkfollowed;
	color:purple;
	text-decoration:underline;}
span.xxxxxxmsohyperlink
	{mso-style-name:x_xxxxxmsohyperlink;
	color:#0563C1;
	text-decoration:underline;}
span.xxxxxxemailstyle23
	{mso-style-name:x_xxxxxemailstyle23;
	font-family:"Nirmala UI",sans-serif;
	color:black;
	font-weight:normal;
	font-style:normal;
	text-decoration:none none;}
span.xxxxxemailstyle26
	{mso-style-name:x_xxxxemailstyle26;
	font-family:"Nirmala UI",sans-serif;
	color:black;
	font-weight:normal;
	font-style:normal;
	text-decoration:none none;}
span.xxxxemailstyle33
	{mso-style-name:x_xxxemailstyle33;
	font-family:"Nirmala UI",sans-serif;
	color:black;
	font-weight:normal;
	font-style:normal;
	text-decoration:none none;}
span.xxxemailstyle40
	{mso-style-name:x_xxemailstyle40;
	font-family:"Nirmala UI",sans-serif;
	color:black;
	font-weight:normal;
	font-style:normal;
	text-decoration:none none;}
span.xxemailstyle47
	{mso-style-name:x_xemailstyle47;
	font-family:"Nirmala UI",sans-serif;
	color:black;
	font-weight:normal;
	font-style:normal;
	text-decoration:none none;}
span.xemailstyle54
	{mso-style-name:x_emailstyle54;
	font-family:"Nirmala UI",sans-serif;
	color:black;
	font-weight:normal;
	font-style:normal;
	text-decoration:none none;}
span.EmailStyle60
	{mso-style-type:personal-reply;
	font-family:"Nirmala UI",sans-serif;
	color:black;
	font-weight:normal;
	font-style:normal;
	text-decoration:none none;}
.MsoChpDefault
	{mso-style-type:export-only;
	font-size:10.0pt;}
@page WordSection1
	{size:612.0pt 792.0pt;
	margin:72.0pt 72.0pt 72.0pt 72.0pt;}
div.WordSection1
	{page:WordSection1;}
--></style><!--[if gte mso 9]><xml>
<o:shapedefaults v:ext="edit" spidmax="1026" />
</xml><![endif]--><!--[if gte mso 9]><xml>
<o:shapelayout v:ext="edit">
<o:idmap v:ext="edit" data="1" />
</o:shapelayout></xml><![endif]-->
</head>
<body lang="EN-GB" link="#0563C1" vlink="purple" style="word-wrap:break-word">
<div class="WordSection1">
''' + html + '</div></body></html>'

print(html)
