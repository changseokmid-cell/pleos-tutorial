from pathlib import Path
import os,subprocess,hashlib,json,shutil,zipfile,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
LAB=Path(os.environ['LOCALAPPDATA'])/'PleosSyncLab'
APK=LAB/'tutorial-build/outputs/apk/release/app-release.apk'
OUT=ROOT/'evidence/build';OUT.mkdir(parents=True,exist_ok=True)
BASE='4fe8a913b52770218757791bf1749c2fb8b35ef9'
assert not subprocess.check_output(['git','-C',str(ROOT),'diff',BASE,'--','android']), 'Android changed since release build'
env=os.environ.copy();env['JAVA_HOME']=str(LAB/'jdk')
cert=subprocess.check_output([str(LAB/'sdk/build-tools/35.0.0/apksigner.bat'),'verify','--verbose','--print-certs',str(APK)],env=env,timeout=60).decode('utf8','replace').replace('\r\n','\n')
(OUT/'signature-verification.txt').write_text(cert,encoding='utf8')
manifest=subprocess.check_output([str(LAB/'sdk/build-tools/35.0.0/aapt2.exe'),'dump','xmltree',str(APK),'--file','AndroidManifest.xml'],timeout=30).decode('utf8','replace').replace('\r\n','\n')
assert 'TestReceiver' not in manifest,'Debug receiver leaked'
assert 'android:debuggable' not in manifest or 'android:debuggable(0x0101000f)=false' in manifest, 'Debug flag present; inspect manifest'
with zipfile.ZipFile(APK) as z:
    assert 'assets/stt-test.pcm' not in z.namelist(),'Debug PCM leaked'
    assert 'assets/schema.json' in z.namelist(),'Gleo schema missing'
    schema=json.loads(z.read('assets/schema.json'))
(OUT/'release-manifest.txt').write_text(manifest,encoding='utf8')
report=LAB/'tutorial-build/test-results/testDebugUnitTest/TEST-kr.pleosguide.GuideSafetyTest.xml'
xml=E.parse(report).getroot()
assert xml.get('tests')=='9' and xml.get('failures')=='0' and xml.get('errors')=='0',xml.attrib
shutil.copy2(report,OUT/report.name)
target=ROOT/'apk/PleosTutorial-1.0.0.apk';shutil.copy2(APK,target)
digest=hashlib.sha256(APK.read_bytes()).hexdigest()
data=dict(sourceCommit=BASE,apkSha256=digest,apkBytes=APK.stat().st_size,signed=True,debuggable=False,debugReceiverIncluded=False,testPcmIncluded=False,gleoSchemaIncluded=True,unitTests=dict(xml.attrib),androidDiffFromSourceCommit='empty')
(OUT/'release-audit.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(data,ensure_ascii=False,indent=2))
