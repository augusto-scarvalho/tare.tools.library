from pathlib import Path
import unittest, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from tare_tools_publisher.policy import validate, route

class PolicyTests(unittest.TestCase):
 def base(self):
  return {'packet_version':'1.0','document_id':'research.workflow.x','document_type':'research','status':'RESEARCH','repository':'tare.tools.research','bounded_contexts':['Workflow'],'artifacts':['x.md'],'canonical_change':False}
 def test_research_route(self): self.assertEqual(route(self.base()),'research/03_workflow/research-workflow-x')
 def test_no_target_in_research(self):
  m=self.base();m['status']='TARGET';self.assertTrue(validate(m))
 def test_canonical_requires_promotion(self):
  m=self.base();m.update(document_type='adr',status='TARGET',repository='tare-tools',canonical_change=True)
  self.assertTrue(validate(m));m['promotion_packet']='promotion/123.json';self.assertFalse(validate(m))
if __name__=='__main__':unittest.main()
