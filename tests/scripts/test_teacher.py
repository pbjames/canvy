from pathlib import Path

import pytest
from agno.document import Document
from agno.document.reader.pdf_reader import PDFReader
from agno.knowledge.pdf import PDFKnowledgeBase
from canvy.const import PS_DIRNAME
from canvy.scripts import teacher
from canvy.scripts.teacher import (
    canvas_files,
    make_problem_sheet,
    retrieve_knowledge,
    validate_typst,
)

from tests.conftest import OPENAI_TEST_KEY, vanilla_config


def test_validate_typst():
    assert validate_typst("content")[0]


def test_validate_typst_failure():
    res, body = validate_typst("#func(")
    assert not res and b"error: unclosed delimiter" in body


def test_make_problem_sheet(tmp_path: Path):
    config = vanilla_config(tmp_path)
    func = make_problem_sheet(config)
    func(
        "test.pdf",
        "class",
        "title",
        # INFO: This content is only valid because of the # -> = conversion
        """
# hello everynyan
## how are you
### fine thank you
""",
    )
    file_bytes = (tmp_path / PS_DIRNAME / "test.pdf").read_bytes()
    assert b"hello everynyan" in file_bytes
    assert b"how are you" in file_bytes
    assert b"fine thank you" in file_bytes


def test_make_problem_sheet_fail(tmp_path: Path):
    config = vanilla_config(tmp_path)
    func = make_problem_sheet(config)
    body = func("test.pdf", "class", "title", "$")
    assert "error" in body


def test_canvas_files(tmp_path: Path):
    config = vanilla_config(tmp_path)
    base = tmp_path / "canvy"
    base.mkdir()
    path_file1 = base / "test1.pdf"
    path_file1.touch()
    path_file2 = base / "cool_course1" / "test2.jpg"
    path_file2.parent.mkdir()
    path_file2.touch()
    path_dir = base / "cool_course2"
    path_dir.mkdir()
    files = canvas_files(config)()
    assert str(path_file1.name) in files
    assert str(path_file2.name) in files
    assert str(path_dir.name) not in files


def test_retrieve_knowledge(tmp_path: Path):
    config = vanilla_config(tmp_path)
    queue: list[Document] = []
    retriever = retrieve_knowledge(config, queue)
    base = tmp_path / "canvy"
    base.mkdir()
    path_file1 = base / "test1.pdf"
    path_file1.write_bytes(
        # INFO: PDF file that says "word" since empty doesn't work
        b'%PDF-1.7\n%\x80\x80\x80\x80\n\n4 0 obj\n<<\n  /Type /Font\n  /Subtype /Type0\n  /BaseFont /MRXGCC+LibertinusSerif-Regular-Identity-H\n  /Encoding /Identity-H\n  /DescendantFonts [5 0 R]\n  /ToUnicode 7 0 R\n>>\nendobj\n\n5 0 obj\n<<\n  /Type /Font\n  /Subtype /CIDFontType0\n  /BaseFont /MRXGCC+LibertinusSerif-Regular\n  /CIDSystemInfo <<\n    /Registry (Adobe)\n    /Ordering (Identity)\n    /Supplement 0\n  >>\n  /FontDescriptor 6 0 R\n  /DW 0\n  /W [0 0 500 1 1 747 2 2 504 3 3 372 4 4 505.99997]\n>>\nendobj\n\n7 0 obj\n<<\n  /Length 356\n  /Type /CMap\n  /WMode 0\n  /Filter /FlateDecode\n>>\nstream\nx\x9cmR\xcbn\xc20\x10\xbc\xe7+\xb6\x07$z\xa0I\x00\x15\t!\xa46\x14)\x07\x1e"\xa8=\x07{C-\x11\xdb\xb2\x9dC\xfe\xbe~\x05\xaa\xaa\x96\xf2\x98\xdd\xd9\x9dY\xdb\xa3\xa7c5y\xa3\xe2\x82\x93\xd9K\x06\'\xd4\xa2S\x04\'\xc5\xae\x96\xc9h\xb4\x11\xa4k\x91\x9b="E:d\xf5\x12\xa4\x12D\xa3\x81\xa2\xdc\x94\x9c\x19K-9\xb9u\x14\x07\xce\x7f\x94w\xbc2\xfe 8\r(:mDk\x93gfn68\x0e\x01\xf0\x9e\xa0\xa4V\x9c\x99\x1e\xb2gK\xf9D\xa5\x99\xe0K\xc8-\xf8\xe0\xb4\x10\xad3\xa7\x934j@z\xb4\xa2\x95\x15m\x18\xa7**\xc1\xc5\xe9&\xf9\x14(#&"\xff&\xad\x9d\xd2\x15W\xbd6\xd8\x96\xbc\x110\x0b,\xda\xc9\xc8\x04\xbb\xd2\x93\xfd\xd5F\xf50\xf6\xc6\x9e\x81b\x132\x07EQ1~\x85\xf1`\xf6W\xb2\xea\xa4\xbc\xa13\t\x99\x8f"\xa7\xfe\x9b\xba\xe1\xf7u\x8b\x90\xc6\x81\xef\xd18%\xe4\x8f\xd0\xb9\x97\x18\x1b\xa4_;A\x07\x90\x07\x8b\xc4F\xb4\xac\t\xaa\x9a_1Yev\xada\xb5\xb5k\xed\x14\xff\xe4\xe7\xa1\xea\xd2\x90\xefZy\xf6\xdc\xb2\xb3\xecu\xbe\xf6h\x1a\xd06\xa0\x99G\x8bi@y@\x0b\xdf7vp\nn#\xef#\x91N);\xb2\xdfG\xef\xdf\x99e\x1c\xef\x07"\x85tU\xfe\xf1\'9\\\n\x87\x0e\xdb\x1f(.\xd2l\nendstream\nendobj\n\n8 0 obj\n<<\n  /Length 926\n  /Filter /FlateDecode\n  /Subtype /CIDFontType0C\n>>\nstream\nx\x9cEO{L\x1bu\x1c\xbf\xa3\xf4aw+YK\xb3rew\r\x96\xc4\x7f \x1b\xd1h\xa2\xa2DY\xc26\xcc\x1e\x92\x85\x8c\x0c(\x14Z\xa0\x14\x8e\x96\x87M\x81\x96\xbe\xaew=z}2\x9e\x15\x99l\x8a\x9d\xa1\x98iGq>b651\xc6\xe8\x0c&&,\x1a_13\xf8\xc7\xef\xb6\xc3`o/~\x7f|~\xdf\xdf\xf7\xfb\xfb~\x1e0TX\x08\xc10\xac9a6\x18\t\x9b\xb9\xd7>p\xc6H\x98;*N\x1b;\xed=\xad\x840;\xcai\xb9R\n\xc1\xb8C\x08\x84\xc9!\x9c\xa2\x1e "-\xfd\xcd\xc9\xc7J5\xda{w\xc5\x87 \x08\xca\x15\xe5\x11\x96\x1f\xc8\xe3\xee.R&\xb4\xb6\x11\xbdp\xfd\x89\x94C"\x18\x96(\x8e\xd7\xb4[\r\xc6\xbavc\xaf\xcdl\x1by\xc5\xda7B\x98;M6\xdd^Uu\xf8HUE\xd5\xe1\xaa\xa7u\xaf\x9b\x8c\xba=[\xba\x93\x84\xb5\xcb\xd8f\xd3\xd5\xd8m&+1P\tA\x05\x10\x0c\x89\xc6\x92\\\xcd\xd4\\\x12\x14\xc7\xd3S\x97\xe3\x12\xde\x9d\x90brQb\x17y\x82B\xf6]\x91o\xee\xdb\x8c \xfb\xb9\r\xb5(\xff9\x7f\xc4B\xa2b\x9a\xa2h!\x80\xe0\xed)\x01>UBb\x81\xae\x1eFas\x81\xa8\xe0\xb3\x06*\xc7\xfd\xb1\x01\xe7Q\x9f\x13Q\x85\\\xe0\xeek;\x01\xc9O\xff\x95\xaaA5\x88\x80j>"\xde\x91p9\xb5P\xf1\xc2\x0b\xbc\x01"\xf7g\xe2\x9d\xb0\x94o\x02\x1f\xab\xf9j\xc0\x8a\xc1\xef\x12\x05h\x88\rr\x95+p\x04Tn\x83r`\x06r\x11h\xe6\xca\xd4,K\xa5\xbc\xac\xcc\x124\x05;\x8d}t?\xa2\xf7z\xa9A\xd6\x9b\xf5%\\\xa9\xb3\xe0 \x7fK\xe3d\xa3\xde\xb86\x16eg"\xf8? \xb8\xcd\xd3\xe2\xc7\xadi\x16\x07\x07\xc1\xb73k\xb3\xcb\x1bL\xc9C\xb2\xa1\xa0=h\xb1\xb4\xd2\x96Gd?\xf8]\xbdN\xd3\xb3|\xbb\xc6E\xf8\xa9\x89\xd43\xc0\xaa\x19\xce\x86\xe2\xd7\'\x1f\xcb\xb7\x05-D\xd7\xdeF\xd6\x9f\xec\x9d;\xcf:4\xb5|\xedh\x17\x19\x1c}\xb7\xe4y`\x18\xbeF\xcf\\cJ\x14\x8d\xae4W\x94\x86\xd7\xb6\x00\xb3%Z\x03\xad\xea\xf2ox1(\xfbj}q\xe5=\xec\xc3\xab\x0b_\xde@\xff=\r\xf6\xf3\x15u\r}-\x1dXg\xcb\xf0\xa9\x13(h\x04\xe7\xd4[\xd7_\xe4\xf5\xbc\xf2XO\xd3\x93f\xa0\xfc\xf1v\xea\x97_q\x05\x7fl~\x10\xfc\xf5w\xfdMfHy\xe7\xd6K\x9b\xaa)\xf0*\xb8\xa7&3\xc1\x8b\xbe\xb8L\x15\x0b\x93$3\xa1\xb5\x8e\xf7\xbb\x8f\xbaIo\xc8\x11\xf2\xca>\xf1%|\xa7P\xfe\xac\xf4\xb91\x7f\xbd\x1f{`Z\x96\xa6W\xe9L\xe6\xa3`\x1a\xd1?\x0cV\x1b\x1ec~F\x01.U-]L.&\xe7\xb0\x99\xc4\xe2JR\x1b\x8b\x91\xe3Q\\\xf5\xb9+\x92\x1c\x9d\xd5\xbe\xb5\xb8\xb4\x84\xab.\xcd\x8f\\jm24\xb7\xdb0\xd5\x94w\xdc\x17\r\xa3\x8as\xae\xac\xe7mp\'\r\xce_\x9e\x8dSC\xca\xd5-\xd0\xb7\xa9Z\x06\xb7s\xea\xf0d,D{d\xcc@\xd4D\xa1\xd1@\x98fC2U\xf7\x9bs\xe9\xe9\x1b\x91\xbc\xf8t^\xfcx\xd8=\xbf\x8er\x8d\xd2\xaf\'3\x14\x16\xf13nL\x95!\\/;\xdb\x02\xe4D\xc8\x917\xcc0\x14\xa3\xbd\x1aHP/\xa0|\xb1\xd4C\x92\x1e\xcco\x98\xed\xd2\xd65\xdb\x8dmxKK\xff\xc9\x1a\x94/\xbay\x04@\x98jy\xf5\xfd\x85\xcc:\x9e\xf8^=LN8\xc7\xb0\xee\x8en\x07\xa1m8\xf3\x058\xf0\xdd\x85\xcct\n\xcf\xbe\xf3\x01\xb3\xa0\xbd\xb24j[\xc0/8\x18O\x0f\xaa\xf8\x1f\n*\xb1\n\nendstream\nendobj\n\n6 0 obj\n<<\n  /Type /FontDescriptor\n  /FontName /MRXGCC+LibertinusSerif-Regular\n  /Flags 131078\n  /FontBBox [-6275 -256 6171 1125]\n  /ItalicAngle 0\n  /Ascent 894\n  /Descent -246\n  /CapHeight 658\n  /StemV 95.4\n  /FontFile3 8 0 R\n>>\nendobj\n\n2 0 obj\n<<\n  /Type /Page\n  /Parent 9 0 R\n  /MediaBox [0 0 595.2756 841.8898]\n  /Contents 10 0 R\n  /Resources 3 0 R\n  /Annots []\n>>\nendobj\n\n10 0 obj\n<<\n  /Length 109\n  /Filter /FlateDecode\n>>\nstream\nx\x9cMK\xbb\x0e\x82@\x10\xec\xf7+\xa6\x94\xc2cG\xcfcmM\xb4\xb0\xdeN-\xcc\x11\xa8\xa0\x80\x8a\xbf\xe7\nH\xc8d\x9e\xc9\x10Zpf\x11\x8b\x0cfwC\x1e\xa4n\xd3\xad\x9f\xfe\x0b\xf2,\x8a9\x8fR\xbf\x14$\xbc\x93\x87\x0b\xf7W\xa3\xc1RbDc\x81\x1aK\xf0A>\xa7\xaf\xaa\x16\xb2\x82a/\x97\xcd\xaf\xc71V?\xf8[\x9e\xbe\x02\xe3\xb3\x1du\nendstream\nendobj\n\n9 0 obj\n<<\n  /Type /Pages\n  /Count 1\n  /Kids [2 0 R]\n>>\nendobj\n\n11 0 obj\n<<>>\nendobj\n\n12 0 obj\n<<>>\nendobj\n\n13 0 obj\n<<>>\nendobj\n\n3 0 obj\n<<\n  /XObject 11 0 R\n  /Pattern 12 0 R\n  /ExtGState 13 0 R\n  /ColorSpace 14 0 R\n  /Font <<\n    /F0 4 0 R\n  >>\n>>\nendobj\n\n14 0 obj\n<<\n  /d65gray [/ICCBased 1 0 R]\n>>\nendobj\n\n1 0 obj\n<<\n  /Length 266\n  /N 1\n  /Range [0 1]\n  /Filter /FlateDecode\n>>\nstream\nx\x9c}\x8fAK\x02Q\x14\x85\xcf4\x95\x16V\x8b\\\x1a\x0c\x11\xad\n\xa2~@\x84\x90m\xda\xa8AS\xab\xd7\x1bm\xa4\x99azoB\xeaWD\xff\xa0\x16\xb6m\x17\xe4\xa6\x96\xed\x04\xc1\x95n\xc4\xad\x1b\x057"\xcf;\xeaFA\xef\xe3p\xbe\xc5\xb9\x8fs\x01\xcdv\xb8+\x97\r\xc0\xf5\x02\x91J\x9f\x99\xd7\xe6\x8d\x11iBG\x1ck\xd8\xc4\x0e\xe3\xd2\xbf\xcc\x9cgA#YQ\xf2@8\x98\x9a^\rZ\xe8\xd5C\x9byV\xf9\xe7.Z.}m\xfd\xbf\x14\xbe\xefK\xed?,\x9e\x15+\'9\xf9/i\x8f\xfb" o\x91v\x8b\x81O\xacE\x89\xe3\xdcf\x16q\x82\xf8\xe0!\x9bN\x12_\x10\x1b\xae\xf3\xc4\'\xff\x84\rb9\xef*C\x1e\xee$ \x91\x82\xc0\xf3\x9c\xcc\xea(\x93\xa4w\x04\x847\xcf\xde"\xf3\'\xc7\xe3\xad\xd8)\xd5l(\xd5\xdd\x07"\xaf\xc0\xe0M\xa9\xfe\xbbR\x83\x0f@\xafS\xf5G\x9f\t6\xca\xea\xa4\xa5|\x01\xe8|\x02\x1b&\xb0]\x01\xd6o\x87\xd8\x1eI\xec\nendstream\nendobj\n\n15 0 obj\n<<\n  /Creator (Typst 0.13.1)\n  /CreationDate (D:20250427094308+01\'00)\n  /ModDate (D:20250427094308+01\'00)\n>>\nendobj\n\n16 0 obj\n<<\n  /Length 996\n  /Type /Metadata\n  /Subtype /XML\n>>\nstream\n<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?><x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="xmp-writer"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/"  xmlns:xmp="http://ns.adobe.com/xap/1.0/"  xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/"  xmlns:xmpTPg="http://ns.adobe.com/xap/1.0/t/pg/"  xmlns:pdf="http://ns.adobe.com/pdf/1.3/" ><xmp:CreatorTool>Typst 0.13.1</xmp:CreatorTool><xmpMM:DocumentID>p17WuNeoDYhXx/Q4m/UmoA==</xmpMM:DocumentID><xmpMM:InstanceID>p17WuNeoDYhXx/Q4m/UmoA==</xmpMM:InstanceID><dc:format>application/pdf</dc:format><pdf:PDFVersion>1.7</pdf:PDFVersion><dc:language><rdf:Bag><rdf:li>en</rdf:li></rdf:Bag></dc:language><xmpTPg:NPages>1</xmpTPg:NPages><xmpMM:RenditionClass>proof</xmpMM:RenditionClass><xmp:CreateDate>2025-04-27T09:43:08+01:00</xmp:CreateDate><xmp:ModifyDate>2025-04-27T09:43:08+01:00</xmp:ModifyDate></rdf:Description></rdf:RDF></x:xmpmeta><?xpacket end="r"?>\nendstream\nendobj\n\n17 0 obj\n<<\n  /Type /Catalog\n  /Pages 9 0 R\n  /ViewerPreferences <<\n    /Direction /L2R\n  >>\n  /Metadata 16 0 R\n  /Lang (en)\n>>\nendobj\n\nxref\n0 18\n0000000000 65535 f\r\n0000002837 00000 n\r\n0000002200 00000 n\r\n0000002656 00000 n\r\n0000000016 00000 n\r\n0000000195 00000 n\r\n0000001962 00000 n\r\n0000000475 00000 n\r\n0000000933 00000 n\r\n0000002526 00000 n\r\n0000002339 00000 n\r\n0000002590 00000 n\r\n0000002612 00000 n\r\n0000002634 00000 n\r\n0000002785 00000 n\r\n0000003202 00000 n\r\n0000003328 00000 n\r\n0000004413 00000 n\r\ntrailer\n<<\n  /Size 18\n  /Root 17 0 R\n  /Info 15 0 R\n  /ID [(p17WuNeoDYhXx/Q4m/UmoA==) (p17WuNeoDYhXx/Q4m/UmoA==)]\n>>\nstartxref\n4549\n%%EOF'
    )
    retriever(path_file1.relative_to(tmp_path))
    assert queue and isinstance(queue.pop(), Document)


def test_teacher(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from agno.agent.agent import Agent

    config = vanilla_config(tmp_path)
    config.openai_key = OPENAI_TEST_KEY

    def chill_function(*args, **kwargs):
        return

    monkeypatch.setattr(Agent, "__init__", chill_function)
    monkeypatch.setattr(Agent, "print_response", print)
    monkeypatch.setattr("builtins.input", lambda _: "exit")
    with pytest.raises(SystemExit):
        teacher(config, [])


def test_teacher_load_docs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from agno.agent.agent import Agent

    config = vanilla_config(tmp_path)
    config.openai_key = OPENAI_TEST_KEY
    count = 0

    def chill_function(*args, **kwargs):
        return

    def exit_upon_twice(_):
        nonlocal count
        count += 1
        return "" if count < 5 else "exit"

    monkeypatch.setattr(Agent, "__init__", chill_function)
    monkeypatch.setattr(Agent, "print_response", print)
    monkeypatch.setattr(Agent, "knowledge", PDFKnowledgeBase(path=tmp_path))
    monkeypatch.setattr("builtins.input", exit_upon_twice)
    path = tmp_path / "file.pdf"
    path.write_bytes(
        # INFO: PDF file that says "word" since empty doesn't work
        b'%PDF-1.7\n%\x80\x80\x80\x80\n\n4 0 obj\n<<\n  /Type /Font\n  /Subtype /Type0\n  /BaseFont /MRXGCC+LibertinusSerif-Regular-Identity-H\n  /Encoding /Identity-H\n  /DescendantFonts [5 0 R]\n  /ToUnicode 7 0 R\n>>\nendobj\n\n5 0 obj\n<<\n  /Type /Font\n  /Subtype /CIDFontType0\n  /BaseFont /MRXGCC+LibertinusSerif-Regular\n  /CIDSystemInfo <<\n    /Registry (Adobe)\n    /Ordering (Identity)\n    /Supplement 0\n  >>\n  /FontDescriptor 6 0 R\n  /DW 0\n  /W [0 0 500 1 1 747 2 2 504 3 3 372 4 4 505.99997]\n>>\nendobj\n\n7 0 obj\n<<\n  /Length 356\n  /Type /CMap\n  /WMode 0\n  /Filter /FlateDecode\n>>\nstream\nx\x9cmR\xcbn\xc20\x10\xbc\xe7+\xb6\x07$z\xa0I\x00\x15\t!\xa46\x14)\x07\x1e"\xa8=\x07{C-\x11\xdb\xb2\x9dC\xfe\xbe~\x05\xaa\xaa\x96\xf2\x98\xdd\xd9\x9dY\xdb\xa3\xa7c5y\xa3\xe2\x82\x93\xd9K\x06\'\xd4\xa2S\x04\'\xc5\xae\x96\xc9h\xb4\x11\xa4k\x91\x9b="E:d\xf5\x12\xa4\x12D\xa3\x81\xa2\xdc\x94\x9c\x19K-9\xb9u\x14\x07\xce\x7f\x94w\xbc2\xfe 8\r(:mDk\x93gfn68\x0e\x01\xf0\x9e\xa0\xa4V\x9c\x99\x1e\xb2gK\xf9D\xa5\x99\xe0K\xc8-\xf8\xe0\xb4\x10\xad3\xa7\x934j@z\xb4\xa2\x95\x15m\x18\xa7**\xc1\xc5\xe9&\xf9\x14(#&"\xff&\xad\x9d\xd2\x15W\xbd6\xd8\x96\xbc\x110\x0b,\xda\xc9\xc8\x04\xbb\xd2\x93\xfd\xd5F\xf50\xf6\xc6\x9e\x81b\x132\x07EQ1~\x85\xf1`\xf6W\xb2\xea\xa4\xbc\xa13\t\x99\x8f"\xa7\xfe\x9b\xba\xe1\xf7u\x8b\x90\xc6\x81\xef\xd18%\xe4\x8f\xd0\xb9\x97\x18\x1b\xa4_;A\x07\x90\x07\x8b\xc4F\xb4\xac\t\xaa\x9a_1Yev\xada\xb5\xb5k\xed\x14\xff\xe4\xe7\xa1\xea\xd2\x90\xefZy\xf6\xdc\xb2\xb3\xecu\xbe\xf6h\x1a\xd06\xa0\x99G\x8bi@y@\x0b\xdf7vp\nn#\xef#\x91N);\xb2\xdfG\xef\xdf\x99e\x1c\xef\x07"\x85tU\xfe\xf1\'9\\\n\x87\x0e\xdb\x1f(.\xd2l\nendstream\nendobj\n\n8 0 obj\n<<\n  /Length 926\n  /Filter /FlateDecode\n  /Subtype /CIDFontType0C\n>>\nstream\nx\x9cEO{L\x1bu\x1c\xbf\xa3\xf4aw+YK\xb3rew\r\x96\xc4\x7f \x1b\xd1h\xa2\xa2DY\xc26\xcc\x1e\x92\x85\x8c\x0c(\x14Z\xa0\x14\x8e\x96\x87M\x81\x96\xbe\xaew=z}2\x9e\x15\x99l\x8a\x9d\xa1\x98iGq>b651\xc6\xe8\x0c&&,\x1a_13\xf8\xc7\xef\xb6\xc3`o/~\x7f|~\xdf\xdf\xf7\xfb\xfb~\x1e0TX\x08\xc10\xac9a6\x18\t\x9b\xb9\xd7>p\xc6H\x98;*N\x1b;\xed=\xad\x840;\xcai\xb9R\n\xc1\xb8C\x08\x84\xc9!\x9c\xa2\x1e "-\xfd\xcd\xc9\xc7J5\xda{w\xc5\x87 \x08\xca\x15\xe5\x11\x96\x1f\xc8\xe3\xee.R&\xb4\xb6\x11\xbdp\xfd\x89\x94C"\x18\x96(\x8e\xd7\xb4[\r\xc6\xbavc\xaf\xcdl\x1by\xc5\xda7B\x98;M6\xdd^Uu\xf8HUE\xd5\xe1\xaa\xa7u\xaf\x9b\x8c\xba=[\xba\x93\x84\xb5\xcb\xd8f\xd3\xd5\xd8m&+1P\tA\x05\x10\x0c\x89\xc6\x92\\\xcd\xd4\\\x12\x14\xc7\xd3S\x97\xe3\x12\xde\x9d\x90brQb\x17y\x82B\xf6]\x91o\xee\xdb\x8c \xfb\xb9\r\xb5(\xff9\x7f\xc4B\xa2b\x9a\xa2h!\x80\xe0\xed)\x01>UBb\x81\xae\x1eFas\x81\xa8\xe0\xb3\x06*\xc7\xfd\xb1\x01\xe7Q\x9f\x13Q\x85\\\xe0\xeek;\x01\xc9O\xff\x95\xaaA5\x88\x80j>"\xde\x91p9\xb5P\xf1\xc2\x0b\xbc\x01"\xf7g\xe2\x9d\xb0\x94o\x02\x1f\xab\xf9j\xc0\x8a\xc1\xef\x12\x05h\x88\rr\x95+p\x04Tn\x83r`\x06r\x11h\xe6\xca\xd4,K\xa5\xbc\xac\xcc\x124\x05;\x8d}t?\xa2\xf7z\xa9A\xd6\x9b\xf5%\\\xa9\xb3\xe0 \x7fK\xe3d\xa3\xde\xb86\x16eg"\xf8? \xb8\xcd\xd3\xe2\xc7\xadi\x16\x07\x07\xc1\xb73k\xb3\xcb\x1bL\xc9C\xb2\xa1\xa0=h\xb1\xb4\xd2\x96Gd?\xf8]\xbdN\xd3\xb3|\xbb\xc6E\xf8\xa9\x89\xd43\xc0\xaa\x19\xce\x86\xe2\xd7\'\x1f\xcb\xb7\x05-D\xd7\xdeF\xd6\x9f\xec\x9d;\xcf:4\xb5|\xedh\x17\x19\x1c}\xb7\xe4y`\x18\xbeF\xcf\\cJ\x14\x8d\xae4W\x94\x86\xd7\xb6\x00\xb3%Z\x03\xad\xea\xf2ox1(\xfbj}q\xe5=\xec\xc3\xab\x0b_\xde@\xff=\r\xf6\xf3\x15u\r}-\x1dXg\xcb\xf0\xa9\x13(h\x04\xe7\xd4[\xd7_\xe4\xf5\xbc\xf2XO\xd3\x93f\xa0\xfc\xf1v\xea\x97_q\x05\x7fl~\x10\xfc\xf5w\xfdMfHy\xe7\xd6K\x9b\xaa)\xf0*\xb8\xa7&3\xc1\x8b\xbe\xb8L\x15\x0b\x93$3\xa1\xb5\x8e\xf7\xbb\x8f\xbaIo\xc8\x11\xf2\xca>\xf1%|\xa7P\xfe\xac\xf4\xb91\x7f\xbd\x1f{`Z\x96\xa6W\xe9L\xe6\xa3`\x1a\xd1?\x0cV\x1b\x1ec~F\x01.U-]L.&\xe7\xb0\x99\xc4\xe2JR\x1b\x8b\x91\xe3Q\\\xf5\xb9+\x92\x1c\x9d\xd5\xbe\xb5\xb8\xb4\x84\xab.\xcd\x8f\\jm24\xb7\xdb0\xd5\x94w\xdc\x17\r\xa3\x8as\xae\xac\xe7mp\'\r\xce_\x9e\x8dSC\xca\xd5-\xd0\xb7\xa9Z\x06\xb7s\xea\xf0d,D{d\xcc@\xd4D\xa1\xd1@\x98fC2U\xf7\x9bs\xe9\xe9\x1b\x91\xbc\xf8t^\xfcx\xd8=\xbf\x8er\x8d\xd2\xaf\'3\x14\x16\xf13nL\x95!\\/;\xdb\x02\xe4D\xc8\x917\xcc0\x14\xa3\xbd\x1aHP/\xa0|\xb1\xd4C\x92\x1e\xcco\x98\xed\xd2\xd65\xdb\x8dmxKK\xff\xc9\x1a\x94/\xbay\x04@\x98jy\xf5\xfd\x85\xcc:\x9e\xf8^=LN8\xc7\xb0\xee\x8en\x07\xa1m8\xf3\x058\xf0\xdd\x85\xcct\n\xcf\xbe\xf3\x01\xb3\xa0\xbd\xb24j[\xc0/8\x18O\x0f\xaa\xf8\x1f\n*\xb1\n\nendstream\nendobj\n\n6 0 obj\n<<\n  /Type /FontDescriptor\n  /FontName /MRXGCC+LibertinusSerif-Regular\n  /Flags 131078\n  /FontBBox [-6275 -256 6171 1125]\n  /ItalicAngle 0\n  /Ascent 894\n  /Descent -246\n  /CapHeight 658\n  /StemV 95.4\n  /FontFile3 8 0 R\n>>\nendobj\n\n2 0 obj\n<<\n  /Type /Page\n  /Parent 9 0 R\n  /MediaBox [0 0 595.2756 841.8898]\n  /Contents 10 0 R\n  /Resources 3 0 R\n  /Annots []\n>>\nendobj\n\n10 0 obj\n<<\n  /Length 109\n  /Filter /FlateDecode\n>>\nstream\nx\x9cMK\xbb\x0e\x82@\x10\xec\xf7+\xa6\x94\xc2cG\xcfcmM\xb4\xb0\xdeN-\xcc\x11\xa8\xa0\x80\x8a\xbf\xe7\nH\xc8d\x9e\xc9\x10Zpf\x11\x8b\x0cfwC\x1e\xa4n\xd3\xad\x9f\xfe\x0b\xf2,\x8a9\x8fR\xbf\x14$\xbc\x93\x87\x0b\xf7W\xa3\xc1RbDc\x81\x1aK\xf0A>\xa7\xaf\xaa\x16\xb2\x82a/\x97\xcd\xaf\xc71V?\xf8[\x9e\xbe\x02\xe3\xb3\x1du\nendstream\nendobj\n\n9 0 obj\n<<\n  /Type /Pages\n  /Count 1\n  /Kids [2 0 R]\n>>\nendobj\n\n11 0 obj\n<<>>\nendobj\n\n12 0 obj\n<<>>\nendobj\n\n13 0 obj\n<<>>\nendobj\n\n3 0 obj\n<<\n  /XObject 11 0 R\n  /Pattern 12 0 R\n  /ExtGState 13 0 R\n  /ColorSpace 14 0 R\n  /Font <<\n    /F0 4 0 R\n  >>\n>>\nendobj\n\n14 0 obj\n<<\n  /d65gray [/ICCBased 1 0 R]\n>>\nendobj\n\n1 0 obj\n<<\n  /Length 266\n  /N 1\n  /Range [0 1]\n  /Filter /FlateDecode\n>>\nstream\nx\x9c}\x8fAK\x02Q\x14\x85\xcf4\x95\x16V\x8b\\\x1a\x0c\x11\xad\n\xa2~@\x84\x90m\xda\xa8AS\xab\xd7\x1bm\xa4\x99azoB\xeaWD\xff\xa0\x16\xb6m\x17\xe4\xa6\x96\xed\x04\xc1\x95n\xc4\xad\x1b\x057"\xcf;\xeaFA\xef\xe3p\xbe\xc5\xb9\x8fs\x01\xcdv\xb8+\x97\r\xc0\xf5\x02\x91J\x9f\x99\xd7\xe6\x8d\x11iBG\x1ck\xd8\xc4\x0e\xe3\xd2\xbf\xcc\x9cgA#YQ\xf2@8\x98\x9a^\rZ\xe8\xd5C\x9byV\xf9\xe7.Z.}m\xfd\xbf\x14\xbe\xefK\xed?,\x9e\x15+\'9\xf9/i\x8f\xfb" o\x91v\x8b\x81O\xacE\x89\xe3\xdcf\x16q\x82\xf8\xe0!\x9bN\x12_\x10\x1b\xae\xf3\xc4\'\xff\x84\rb9\xef*C\x1e\xee$ \x91\x82\xc0\xf3\x9c\xcc\xea(\x93\xa4w\x04\x847\xcf\xde"\xf3\'\xc7\xe3\xad\xd8)\xd5l(\xd5\xdd\x07"\xaf\xc0\xe0M\xa9\xfe\xbbR\x83\x0f@\xafS\xf5G\x9f\t6\xca\xea\xa4\xa5|\x01\xe8|\x02\x1b&\xb0]\x01\xd6o\x87\xd8\x1eI\xec\nendstream\nendobj\n\n15 0 obj\n<<\n  /Creator (Typst 0.13.1)\n  /CreationDate (D:20250427094308+01\'00)\n  /ModDate (D:20250427094308+01\'00)\n>>\nendobj\n\n16 0 obj\n<<\n  /Length 996\n  /Type /Metadata\n  /Subtype /XML\n>>\nstream\n<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?><x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="xmp-writer"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/"  xmlns:xmp="http://ns.adobe.com/xap/1.0/"  xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/"  xmlns:xmpTPg="http://ns.adobe.com/xap/1.0/t/pg/"  xmlns:pdf="http://ns.adobe.com/pdf/1.3/" ><xmp:CreatorTool>Typst 0.13.1</xmp:CreatorTool><xmpMM:DocumentID>p17WuNeoDYhXx/Q4m/UmoA==</xmpMM:DocumentID><xmpMM:InstanceID>p17WuNeoDYhXx/Q4m/UmoA==</xmpMM:InstanceID><dc:format>application/pdf</dc:format><pdf:PDFVersion>1.7</pdf:PDFVersion><dc:language><rdf:Bag><rdf:li>en</rdf:li></rdf:Bag></dc:language><xmpTPg:NPages>1</xmpTPg:NPages><xmpMM:RenditionClass>proof</xmpMM:RenditionClass><xmp:CreateDate>2025-04-27T09:43:08+01:00</xmp:CreateDate><xmp:ModifyDate>2025-04-27T09:43:08+01:00</xmp:ModifyDate></rdf:Description></rdf:RDF></x:xmpmeta><?xpacket end="r"?>\nendstream\nendobj\n\n17 0 obj\n<<\n  /Type /Catalog\n  /Pages 9 0 R\n  /ViewerPreferences <<\n    /Direction /L2R\n  >>\n  /Metadata 16 0 R\n  /Lang (en)\n>>\nendobj\n\nxref\n0 18\n0000000000 65535 f\r\n0000002837 00000 n\r\n0000002200 00000 n\r\n0000002656 00000 n\r\n0000000016 00000 n\r\n0000000195 00000 n\r\n0000001962 00000 n\r\n0000000475 00000 n\r\n0000000933 00000 n\r\n0000002526 00000 n\r\n0000002339 00000 n\r\n0000002590 00000 n\r\n0000002612 00000 n\r\n0000002634 00000 n\r\n0000002785 00000 n\r\n0000003202 00000 n\r\n0000003328 00000 n\r\n0000004413 00000 n\r\ntrailer\n<<\n  /Size 18\n  /Root 17 0 R\n  /Info 15 0 R\n  /ID [(p17WuNeoDYhXx/Q4m/UmoA==) (p17WuNeoDYhXx/Q4m/UmoA==)]\n>>\nstartxref\n4549\n%%EOF'
    )
    doc = PDFReader().read(path)
    with pytest.raises(SystemExit):
        teacher(config, doc)
