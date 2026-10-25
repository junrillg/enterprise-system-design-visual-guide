"""Build editable SVG concept diagrams. Python standard library only."""
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parent
OUT=ROOT
PALETTE={'blue':('#edf4ff','#245b9e'),'green':('#e7f7f1','#137562'),'orange':('#fff3df','#a76012'),'red':('#fff0ef','#af3434'),'gray':('#f1f4f8','#536478')}
class Diagram:
 def __init__(self,name,title,subtitle,h=650):
  self.name=name;self.h=h
  self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{h}" viewBox="0 0 960 {h}" role="img" aria-labelledby="title desc">',f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc>', '<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L8,4 L0,8 Z" fill="#536478"/></marker><marker id="redarr" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L8,4 L0,8 Z" fill="#af3434"/></marker></defs>',f'<rect width="960" height="{h}" rx="20" fill="#fff"/>','<style>text{font-family:Arial,Helvetica,sans-serif} .head{font-size:29px;font-weight:700;fill:#15324f}.sub{font-size:19px;fill:#536478}.boxt{font-size:23px;font-weight:700;fill:#15324f}.body{font-size:19px;fill:#33495d}.label{font-size:18px;fill:#536478}.foot{font-size:18px;fill:#536478}</style>']
  self.text(36,49,title,'head');self.text(36,82,subtitle,'sub')
 def text(self,x,y,s,cls='body',anchor='start',fill=None):
  attr=f' fill="{fill}"' if fill else ''
  self.parts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}"{attr}>{escape(s)}</text>')
 def box(self,x,y,w,h,title,lines=(),kind='blue'):
  bg,stroke=PALETTE[kind]
  self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="13" fill="{bg}" stroke="{stroke}" stroke-width="2"/>')
  self.text(x+w/2,y+33,title,'boxt','middle')
  for i,line in enumerate(lines): self.text(x+w/2,y+62+i*25,line,'body','middle')
 def edge(self,points,label='',pos=None,red=False,dash=False,both=False):
  color='#af3434' if red else '#536478';marker='redarr' if red else 'arr'
  self.parts.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="2.5" marker-end="url(#{marker})"'+(' stroke-dasharray="7 5"' if dash else '')+(' marker-start="url(#arr)"' if both else '')+'/>')
  if label and pos:
   x,y=pos;w=len(label)*9.8+16
   self.parts.append(f'<rect x="{x-w/2}" y="{y-19}" width="{w}" height="25" rx="4" fill="#fff"/>')
   self.text(x,y,label,'label','middle')
 def note(self,y,lines,kind='gray'):
  self.box(36,y,888,17+25*len(lines),'',[],kind)
  for i,l in enumerate(lines): self.text(58,y+30+i*25,l)
 def save(self):
  self.parts.append('</svg>');(OUT/f'{self.name}.svg').write_text('\n'.join(self.parts))

d=Diagram('overview','System design concepts','Guarantees, transaction boundaries, and recovery paths.',720)
d.box(295,120,370,95,'Accept a loan offer',['One customer action'])
d.box(220,285,520,120,'Coordinate the required work',['Transactions define the boundary','Saga + coordination define recovery'],'green')
d.edge([(480,215),(480,285)],'more than one owner',(630,251))
d.box(36,485,278,110,'Remember facts',['Event sourcing','Optional history model'])
d.box(341,485,278,110,'Propagate changes',['CDC + reliable events','Update search / reporting'])
d.box(646,485,278,110,'Serve fast reads',['Distributed cache','Indicative products'])
d.edge([(480,405),(480,445),(175,445),(175,485)])
d.edge([(480,405),(480,485)])
d.edge([(480,405),(480,445),(785,445),(785,485)])
d.text(480,650,'CAP: define what each operation does when communication breaks.','body','middle');d.save()

d=Diagram('transactions','Where does the transaction end?','Same business goal; three different coordination boundaries.',890)
d.text(36,130,'1  One local database', 'boxt')
d.box(70,155,350,100,'Loan + Capacity modules',['One database transaction'],'green')
d.box(570,155,320,100,'One transactional store',['Commit both or neither'],'green');d.edge([(420,205),(570,205)])
d.text(36,315,'2  Two-phase commit', 'boxt')
d.box(325,345,310,82,'Coordinator',['Durable decision'])
d.box(70,500,330,100,'Loan database',['Prepared participant'])
d.box(560,500,330,100,'Capacity database',['Prepared participant'])
d.edge([(325,386),(235,386),(235,500)],'prepare / decide',(225,462))
d.edge([(635,386),(725,386),(725,500)],'prepare / decide',(735,462))
d.text(480,635,'A prepared participant may wait if it cannot learn the decision.','body','middle')
d.text(36,695,'3  Saga', 'boxt')
d.box(70,720,330,100,'Reserve capacity',['Local commit'],'green')
d.box(560,720,330,100,'Prepare agreement',['Local commit or failure'],'orange')
d.edge([(400,750),(560,750)],'next step',(480,739))
d.edge([(560,798),(400,798)],'compensate',(480,832),red=True,dash=True);d.save()

d=Diagram('event-sourcing','Events as the source of truth','Current state and read models are derived from the loan stream.',680)
d.box(36,145,275,115,'AcceptOffer command',['Validate current state','Append at expected version'])
d.box(510,125,414,205,'Loan event stream',['v1  OfferAccepted','v2  CapacityReserved','v3  AgreementPrepared','v4  LoanActivated'],'green')
d.edge([(311,200),(510,200)],'atomic append',(410,183))
d.box(36,425,375,115,'Rehydrated loan',['Apply ordered facts','Used to validate a command'])
d.box(549,425,375,115,'Dashboard projection',['Query-friendly view','May lag behind the stream'])
d.edge([(615,330),(615,373),(224,373),(224,425)],'replay',(363,361))
d.edge([(737,330),(737,425)],'project',(800,384))
d.note(575,['Snapshot = saved derived state at a stream version.','Rebuilds must not repeat emails or external money movements.']);d.save()

d=Diagram('cdc','A committed row change reaches search','CDC exposes changes; a consumer applies them to a target.',610)
d.box(36,165,264,125,'Legacy database',['Loan status commits','Source of truth'])
d.box(348,165,264,125,'Capture + position',['Log / change tables','Resume from checkpoint'])
d.box(660,165,264,125,'Indexer',['Upsert / delete','Handle duplicate delivery'],'green')
d.edge([(300,228),(348,228)]);d.edge([(612,228),(660,228)])
d.box(660,395,264,100,'Search view',['Eventually updated'],'green')
d.edge([(792,290),(792,395)],'apply change',(868,351))
d.box(36,395,500,100,'Initial snapshot + stream handoff',['Must avoid gaps while copying existing rows'],'orange')
d.note(520,['Raw CDC describes committed storage changes.','Capturing an outbox can carry deliberate business meaning.']);d.save()

d=Diagram('saga','The failure path is part of the design','Agreement failure does not erase a committed reservation.',790)
d.box(300,135,360,100,'Reserve capacity',['Reservation R123 committed'],'green')
d.box(300,305,360,100,'Prepare agreement',['Rejected: invalid input'],'orange')
d.edge([(480,235),(480,305)],'forward work',(611,274))
d.box(300,485,360,100,'Release R123',['New local transaction'],'red')
d.edge([(480,405),(480,485)],'compensate',(600,451),red=True)
d.box(36,650,360,85,'Cancelled',['Release confirmed'],'green')
d.box(564,650,360,85,'Compensating / review',['Release failed; retain recovery state'],'orange')
d.edge([(380,585),(380,615),(216,615),(216,650)],'success',(249,603))
d.edge([(580,585),(580,615),(744,615),(744,650)],'failure',(738,603),red=True)
d.text(480,768,'Never report completed cancellation while the reservation is still held.','body','middle');d.save()

d=Diagram('choreography','Choreography: reactions decide the next step','No central workflow owner; the event contracts still define a flow.',700)
d.box(36,155,264,110,'Loan',['Offer accepted','Publishes fact'])
d.box(348,155,264,110,'Capacity',['Reserve R123','Publish result'],'green')
d.box(660,155,264,110,'Agreements',['Prepare draft','Publish result'])
d.edge([(300,210),(348,210)]);d.edge([(612,210),(660,210)])
d.text(170,307,'OfferAccepted','body','middle');d.text(480,307,'CapacityReserved','body','middle')
d.box(660,420,264,100,'Preparation failed',['Failure fact'],'orange')
d.box(348,420,264,100,'Capacity subscriber',['Release R123'],'red')
d.edge([(792,265),(792,420)],'failure',(866,366))
d.edge([(660,470),(612,470)],'react',(636,550),red=True)
d.note(575,['A successful preparation could trigger activation through another subscriber.','Someone must still own deadlines, late events, and stuck-work investigation.']);d.save()

d=Diagram('orchestration','Orchestration: one workflow owns sequence','Participants keep their rules and data; the workflow directs recovery.',660)
d.box(265,140,430,120,'Durable activation workflow',['1 Reserve  →  2 Prepare  →  3 Activate','On failure: coordinate compensation'],'green')
d.box(36,430,264,110,'Capacity',['Owns reservation rule','Its own local commit'])
d.box(348,430,264,110,'Agreements',['Owns draft agreement','Its own local commit'])
d.box(660,430,264,110,'Loan',['Owns legal state','Its own local commit'])
d.edge([(335,260),(335,330),(168,330),(168,430)],'command / result',(172,367),both=True)
d.edge([(480,260),(480,430)],'command / result',(480,367),both=True)
d.edge([(625,260),(625,330),(792,330),(792,430)],'command / result',(788,367),both=True)
d.note(575,['Commands and results can travel through durable messages.','Logical central coordination does not require one unreplicated process.']);d.save()

d=Diagram('cap','A network split forces a decision','Capacity was 100. Two isolated sides each receive a request for 80.',780)
d.box(36,155,360,120,'Side A',['Last known capacity: 100','Client asks to reserve 80'])
d.box(564,155,360,120,'Side B',['Last known capacity: 100','Client asks to reserve 80'])
d.edge([(396,215),(564,215)],'link unavailable',(480,195),red=True,dash=True)
d.text(36,347,'If both independently accept', 'boxt')
d.box(36,375,888,100,'80 + 80 = 160 reserved',['Unsafe without preallocated independent reservation rights'],'red')
d.text(36,547,'One correctness-preserving policy', 'boxt')
d.box(36,575,420,100,'Authoritative side',['May accept within available capacity'],'green')
d.box(504,575,420,100,'Isolated side',['Defer or reject the reservation'],'orange')
d.note(695,['Preserve the rule, but some requests lose availability during the partition.']);d.save()

d=Diagram('cache','Fast shared reads, authoritative decisions','Cache indicative products; validate binding terms and scarce capacity.',685)
d.box(36,145,270,100,'API instance A',['Same cache key policy'])
d.box(36,305,270,100,'API instance B',['Tenant-scoped requests'])
d.box(510,195,414,120,'Shared cache',['Hit: return indicative products','Miss: API loads the catalog'],'green')
d.box(510,470,414,110,'Authoritative database',['Committed product / offer versions','Capacity reservation is decided here'])
d.edge([(306,195),(410,195),(410,235),(510,235)],'lookup',(408,175))
d.edge([(306,355),(410,355),(410,275),(510,275)])
d.edge([(717,315),(717,470)],'on miss: API loads DB',(717,397))
d.note(605,['Expiry + invalidation reduce staleness; they do not create a global transaction.']);d.save()

d=Diagram('outbox','Outbox saves intent; inbox protects the local effect','Two separate crash windows need two separate solutions.',760)
d.box(36,145,370,140,'One source transaction',['Loan acceptance','+ outgoing event E123','Commit both together'],'green')
d.box(570,145,354,140,'Relay / broker',['Publish E123','May publish it again'])
d.edge([(406,215),(570,215)],'after commit',(486,195))
d.box(570,425,354,150,'One consumer transaction',['Claim E123 for this handler','+ local business mutation','Commit before acknowledgment'],'green')
d.edge([(747,285),(747,425)],'deliver / redeliver',(747,363))
d.box(36,425,370,150,'Consumer crash cases',['Before commit: retry all','After commit: inbox suppresses','the repeated local effect'])
d.note(625,['An external lender API is outside the consumer database transaction.','Use provider idempotency plus durable intent and outcome reconciliation.']);d.save()

d=Diagram('enterprise','Sample transaction flow and reliability boundaries','Base design: current-state tables + reliable events. Event sourcing is optional.',900)
d.box(36,145,264,110,'AcceptOffer API',['Authorize tenant','Validate offer + request key'])
d.box(348,145,264,110,'Loan local commit',['Acceptance + outbox','Atomic request result'],'green')
d.box(660,145,264,110,'Relay + workflow',['Deduplicate start','Persist progress'])
d.edge([(300,200),(348,200)]);d.edge([(612,200),(660,200)])
d.box(660,375,264,110,'Activation saga',['Reserve capacity','Prepare agreement / activate'],'green')
d.edge([(792,255),(792,375)],'required work',(792,322))
d.box(348,375,264,110,'Failure recovery',['Release reservation','Retry or manual review'],'red')
d.edge([(660,430),(612,430)])
d.box(36,375,264,110,'Capacity owner',['Conditional reservation','Never trust a cached count'])
d.edge([(660,470),(636,470),(636,535),(168,535),(168,485)],'local invariant',(415,559))
d.box(36,665,264,110,'Indicative products',['Shared cache','No binding decisions'])
d.box(348,665,264,110,'History, optional',['Event-sourced Loan','Rebuild state safely'])
d.box(660,665,264,110,'Search + reporting',['CDC / committed events','Eventual projection'])
d.edge([(792,485),(792,665)],'after committed work',(792,595))
d.note(805,['CAP policy: defer authoritative writes when coordination cannot be established.']);d.save()
print('Built',len(list(OUT.glob('*.svg'))),'SVG diagrams')
