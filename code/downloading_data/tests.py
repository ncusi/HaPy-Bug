import unittest
import requests

import downloading_diffs
import downloading_cve_data


class TestFunctions(unittest.TestCase):

    def test_getCveJson(self):
        response = requests.get("http://158.75.112.151:5000/api/cve/CVE-2016-3333")
        self.assertEqual(downloading_cve_data.getCveJson("CVE-2016-3333"), response.json())

    def test_getUrls(self):
        self.assertEqual(downloading_diffs.findUrls({}), set())

        d = {"a": {"b": ["https://www.google.pl/"], "c": [{"d": "https://github.com/", "e": "yahoo"}]}}
        self.assertEqual(downloading_diffs.findUrls(d), {"https://www.google.pl/", "https://github.com/"})

        d = requests.get("http://158.75.112.151:5000/api/cve/CVE-2021-3177").json()
        urls = ["https://bugs.python.org/issue42938",
                "https://github.com/python/cpython/pull/24239",
                "https://python-security.readthedocs.io/vuln/ctypes-buffer-overflow-pycarg_repr.html",
                "https://bugs.python.org/issue42938",
                "https://github.com/python/cpython/pull/24239",
                "https://python-security.readthedocs.io/vuln/ctypes-buffer-overflow-pycarg_repr.html",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NQPARTLNSFQVMMQHPNBFOCOZOO3TMQNA/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MGSV6BJQLRQ6RKVUXK7JGU7TP4QFGQXC/",
                "https://security.gentoo.org/glsa/202101-18",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z7GZV74KM72O2PEJN2C4XP3V5Q5MZUOO/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CCFZMVRQUKCBQIG5F2CBVADK63NFSE4A/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BRHOCQYX3QLDGDQGTWQAUUT2GGIZCZUO/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/V6XJAULOS5JVB2L67NCKKMJ5NTKZJBSD/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NXSMBHES3ANXXS2RSO5G6Q24BR4B2PWK/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YDTZVGSXQ7HR7OCGSUHTRNTMBG43OMKU/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Y4KSYYWMGAKOA2JVCQA422OINT6CKQ7O/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FPE7SMXYUIWPOIZV4DQYXODRXMFX3C5E/",
                "https://news.ycombinator.com/item?id=26185005",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HCQTCSP6SCVIYNIRUJC5X7YBVUHPLSC4/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NODWHDIFBQE5RU5PUWUVE47JOT5VCMJ2/",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MP572OLHMS7MZO4KUPSCIMSZIA5IZZ62/",
                "https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772@%3Cdev.mina.apache.org%3E",
                "https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FONHJIOZOFD7CD35KZL6SVBUTMBPGZGA/",
                "https://security.netapp.com/advisory/ntap-20210226-0003/",
                "https://lists.debian.org/debian-lts-announce/2021/04/msg00005.html",
                "https://www.oracle.com//security-alerts/cpujul2021.html",
                "https://www.oracle.com/security-alerts/cpuoct2021.html",
                "https://www.oracle.com/security-alerts/cpujan2022.html",
                "https://lists.debian.org/debian-lts-announce/2022/02/msg00013.html",
                "https://www.oracle.com/security-alerts/cpujul2022.html"]
        self.assertEqual(downloading_diffs.findUrls(d), set(urls))


unittest.main(argv=[''], verbosity=2, exit=False)
