# curators-eye: 10 sample rows for review

Built by `data_gen/build_dataset.py` from `data_gen/specs/samples.json`. Each row's
`answer` holds the intruder IDs, and `info` holds the hidden theme, decoy, tier, and every item's truth.

## Exact prompt the model sees (row 1)

```text
[system]
You are a curator reviewing a collection. Every item was chosen according to a single organizing principle, which is never stated. One or two items are intruders: they look like they belong, but they violate the principle.

Identify the intruder(s) and name the organizing principle. Respond in exactly this format:
<intruders>comma-separated item IDs</intruders>
<theme>one sentence stating the organizing principle</theme>

[user]
The collection:

A. Oware: Seeds are sown around a ring of pits, capturing on certain counts.
B. Abalone: Marbles shove each other off the edge of a hexagonal board.
C. Hive: Hexagonal insect pieces form the playing surface as they are placed.
D. Chess: Two armies of sixteen pieces maneuver across an 8x8 checkered board.
E. Scrabble: Build interlocking words on a grid of premium squares for points.
F. Checkers: Discs move diagonally and capture by jumping over opponents.
G. Backgammon: Race fifteen checkers around triangular points and bear them off.
H. Nine Men's Morris: Form rows of three on nested squares to remove enemy pieces.
I. Go: Stones are placed alternately on a grid to surround territory.
J. Connect Four: Drop discs into a vertical rack to line up four in a row.
K. Othello: Discs flip between two colors when outflanked along a line.
```

## 1. [obvious] games: `games-zero-chance`

**Hidden theme:** Games with no element of chance: no dice, card draws, or blind tile pulls, so outcomes depend only on the players' decisions.  
**Decoy (what the intruders also satisfy):** Classic tabletop strategy games  
**answer:** `E,G`

| ID | Item | Description | |
|---|---|---|---|
| A | Oware | Seeds are sown around a ring of pits, capturing on certain counts. |  |
| B | Abalone | Marbles shove each other off the edge of a hexagonal board. |  |
| C | Hive | Hexagonal insect pieces form the playing surface as they are placed. |  |
| D | Chess | Two armies of sixteen pieces maneuver across an 8x8 checkered board. |  |
| E | Scrabble | Build interlocking words on a grid of premium squares for points. | **INTRUDER** |
| F | Checkers | Discs move diagonally and capture by jumping over opponents. |  |
| G | Backgammon | Race fifteen checkers around triangular points and bear them off. | **INTRUDER** |
| H | Nine Men's Morris | Form rows of three on nested squares to remove enemy pieces. |  |
| I | Go | Stones are placed alternately on a grid to surround territory. |  |
| J | Connect Four | Drop discs into a vertical rack to line up four in a row. |  |
| K | Othello | Discs flip between two colors when outflanked along a line. |  |

- **E Scrabble**: Letter tiles are drawn blind from a bag, so each rack is luck.
- **G Backgammon**: Every move is dictated by a roll of two dice.

## 2. [obvious] music: `music-woodwinds`

**Hidden theme:** Woodwind instruments: the sound comes from a reed or from air split across an edge, whatever the body is made of.  
**Decoy (what the intruders also satisfy):** Orchestral and band wind instruments  
**answer:** `F`

| ID | Item | Description | |
|---|---|---|---|
| A | Bassoon | Tall folded instrument with a long curved metal crook. |  |
| B | English horn | Alto instrument with a bulb-shaped bell, pitched a fifth below its smaller sibling. |  |
| C | Oboe | Slender conical instrument whose pitch tunes the orchestra. |  |
| D | Recorder | Wooden or plastic end-blown pipe common in school music classes. |  |
| E | Flute | Metal tube held sideways and played by blowing over an open hole. |  |
| F | French horn | Coiled metal instrument ending in a wide bell, played with a hand inside it. | **INTRUDER** |
| G | Saxophone | Brass-bodied conical instrument with a curved neck and upturned bell. |  |
| H | Piccolo | Half-sized, highest-pitched voice of the orchestra's wind section. |  |
| I | Clarinet | Black cylindrical instrument with a beaked mouthpiece and flared bell. |  |

- **F French horn**: A brass instrument: the player's lips buzz in a cup mouthpiece. Its name echoes the English horn, which is a woodwind.

## 3. [obvious] tools: `tools-kitchen-cutting`

**Hidden theme:** Kitchen tools that work by cutting: a blade, sharp edge, or taut wire severs the food.  
**Decoy (what the intruders also satisfy):** Handheld gadgets for preparing produce and ingredients  
**answer:** `E,G`

| ID | Item | Description | |
|---|---|---|---|
| A | Mezzaluna | Curved rocking tool with handles at both ends, used on herbs. |  |
| B | Egg slicer | Hinged frame that divides a boiled egg into even rounds. |  |
| C | Mandoline | Flat frame with an adjustable platform for uniform thin pieces. |  |
| D | Microplane zester | Long rasp that lifts fine strands from citrus peel and hard cheese. |  |
| E | Potato ricer | Lever-operated hopper that pushes cooked potatoes through small holes. | **INTRUDER** |
| F | Poultry shears | Heavy spring-loaded scissors for jointing birds. |  |
| G | Garlic press | Hinged tool that forces cloves through a perforated chamber. | **INTRUDER** |
| H | Pizza wheel | Rolling disc on a handle for portioning flatbreads. |  |
| I | Apple corer | Ringed tube pushed through fruit to remove the center. |  |
| J | Cheese plane | Flat spatula with a slot that shaves thin sheets from a block. |  |
| K | Spiralizer | Crank-turned gadget that turns vegetables into long ribbons. |  |

- **E Potato ricer**: It extrudes soft food through a plate rather than cutting it.
- **G Garlic press**: It crushes and extrudes; nothing in it has a cutting edge.

## 4. [moderate] architecture: `architecture-expo-built`

**Hidden theme:** Structures originally built for a world's fair or international exposition.  
**Decoy (what the intruders also satisfy):** Iconic modern landmarks and towers  
**answer:** `G`

| ID | Item | Description | |
|---|---|---|---|
| A | Space Needle | Observation tower with a saucer-shaped top in Seattle. |  |
| B | Habitat 67 | Stacked prefabricated concrete boxes forming a housing complex in Montreal. |  |
| C | Atomium | Nine steel-clad spheres joined by tubes, in Brussels. |  |
| D | Palace of Fine Arts | Roman-style rotunda and colonnade beside a lagoon in San Francisco. |  |
| E | Tower of the Americas | Slender concrete tower topped by a revolving restaurant in San Antonio. |  |
| F | Crystal Palace | Vast cast-iron and plate-glass hall first raised in Hyde Park, London. |  |
| G | Beijing National Stadium | Woven steel-lattice 'Bird's Nest' arena in Beijing. | **INTRUDER** |
| H | Montreal Biosphere | Buckminster Fuller geodesic dome on an island in the St. Lawrence. |  |
| I | Eiffel Tower | Wrought-iron lattice tower on the Champ de Mars in Paris. |  |
| J | Barcelona Pavilion | Mies van der Rohe's low hall of marble, onyx, glass, and chrome columns. |  |

- **G Beijing National Stadium**: Built for the 2008 Olympics: a major international event, but a sporting one, not an exposition.

## 5. [moderate] food: `food-named-for-a-person`

**Hidden theme:** Dishes named after a specific real person.  
**Decoy (what the intruders also satisfy):** Classic restaurant dishes with proper-noun names  
**answer:** `C,K`

| ID | Item | Description | |
|---|---|---|---|
| A | Caesar salad | Romaine with croutons, parmesan, and a coddled-egg dressing. |  |
| B | Oysters Rockefeller | Baked oysters on the half shell under a rich green herb topping. |  |
| C | Chicken Marengo | Chicken braised with tomatoes, garlic, and wine, garnished with crayfish. | **INTRUDER** |
| D | Bananas Foster | Bananas flambeed in butter, brown sugar, and rum, served over ice cream. |  |
| E | Pavlova | Meringue with a crisp crust and soft center, topped with fruit and cream. |  |
| F | Chicken Tetrazzini | Baked pasta and chicken in a creamy mushroom-and-sherry sauce. |  |
| G | Beef Stroganoff | Sauteed strips of beef in a sour-cream sauce. |  |
| H | Peach Melba | Poached peaches with raspberry sauce over vanilla ice cream. |  |
| I | Salisbury steak | Seasoned ground-beef patty served in brown gravy. |  |
| J | Carpaccio | Paper-thin slices of raw beef dressed with oil and shaved cheese. |  |
| K | Lobster Thermidor | Lobster in a cognac-cream sauce, returned to the shell and browned. | **INTRUDER** |
| L | Nachos | Tortilla chips baked with melted cheese and sliced jalapenos. |  |

- **C Chicken Marengo**: Named after the Battle of Marengo, a village in Piedmont. It is tied to Napoleon but not named for him.
- **K Lobster Thermidor**: Named after the play 'Thermidor', which takes its name from a month in the French Revolutionary calendar. No person is involved.

## 6. [moderate] games: `games-born-as-mods`

**Hidden theme:** Games that began as fan-made mods of another game.  
**Decoy (what the intruders also satisfy):** Influential PC multiplayer and indie games  
**answer:** `G`

| ID | Item | Description | |
|---|---|---|---|
| A | DayZ | Survivors scavenge a post-Soviet countryside overrun by the infected. |  |
| B | Counter-Strike | Tactical team shooter: one side plants a bomb, the other defuses it. |  |
| C | The Stanley Parable | An office worker defies a narrator in a branching story. |  |
| D | Garry's Mod | Physics sandbox for building contraptions, with no set goals. |  |
| E | Day of Defeat | Second World War squad shooter fought over control points. |  |
| F | Red Orchestra | Unforgiving Eastern Front infantry shooter. |  |
| G | Fortnite | Hundred-player last-one-standing shooter where you build cover on the fly. | **INTRUDER** |
| H | Team Fortress | Class-based team shooter built around capturing flags. |  |
| I | Defense of the Ancients | Three-lane battle in which each player commands a single hero. |  |
| J | Dear Esther | Wander an empty Hebridean island while a narrator reads letters. |  |

- **G Fortnite**: Epic built its battle royale mode in-house. The genre traces back to mods, but this game did not start as one.

## 7. [moderate] internet culture: `internet-screen-still-memes`

**Hidden theme:** Reaction-image memes that are frames taken from a film, TV show, or TV cartoon.  
**Decoy (what the intruders also satisfy):** Famous reaction-image memes  
**answer:** `F`

| ID | Item | Description | |
|---|---|---|---|
| A | Not Sure If | A squinting orange-haired man narrows his eyes in suspicion. |  |
| B | Mocking SpongeBob | A hunched sea sponge clucks, captioned in alternating capital letters. |  |
| C | Picard Facepalm | A bald officer in uniform buries his face in his hand. |  |
| D | Spider-Man Pointing | Two identical costumed heroes point accusingly at each other. |  |
| E | One Does Not Simply | A bearded man at a council gestures while explaining why a task is harder than it sounds. |  |
| F | This Is Fine | A cartoon dog sips coffee calmly while the room around him burns. | **INTRUDER** |
| G | Surprised Pikachu | A yellow creature stares with its mouth hanging open in shock. |  |
| H | Laughing Leo | A man in a velvet jacket laughs, drink in hand, surrounded by guests. |  |
| I | Is This a Pigeon? | A bespectacled man gestures at a butterfly and misidentifies it. |  |

- **F This Is Fine**: Comes from KC Green's webcomic 'Gunshow'. It looks like a cartoon but was never on screen.

## 8. [subtle] design objects: `design-repurposed-products`

**Hidden theme:** Products first made or sold for a completely different use than the one they became famous for.  
**Decoy (what the intruders also satisfy):** Everyday products with well-known invention stories  
**answer:** `E`

| ID | Item | Description | |
|---|---|---|---|
| A | Listerine | Antiseptic mouthwash with a sharp herbal bite. |  |
| B | Silly Putty | Bouncy, stretchy silicone putty packaged in a plastic egg. |  |
| C | Kleenex | Disposable facial tissues pulled from a box. |  |
| D | Rubik's Cube | Twisting 3x3x3 puzzle with six colored faces. |  |
| E | Band-Aid | Adhesive strip with a small gauze pad for minor cuts. | **INTRUDER** |
| F | Coca-Cola | Caramel-colored carbonated soft drink. |  |
| G | Chainsaw | Motorized saw with teeth mounted on a looping chain. |  |
| H | Play-Doh | Soft, brightly colored modeling compound for children. |  |
| I | Bubble Wrap | Sheets of air-filled plastic cushions. |  |

- **E Band-Aid**: Invented for exactly this job, covering kitchen cuts. It has a charming origin story but never changed purpose.

## 9. [subtle] music: `music-bands-named-for-songs`

**Hidden theme:** Bands named after a song by another artist.  
**Decoy (what the intruders also satisfy):** British and American rock bands with borrowed or cryptic names  
**answer:** `F,I`

| ID | Item | Description | |
|---|---|---|---|
| A | The Pretty Things | Raw 1960s R&B band that went on to make an early rock opera. |  |
| B | Radiohead | Oxford band that moved from guitar anthems to glitchy electronics. |  |
| C | Death Cab for Cutie | Washington State indie band fronted by Ben Gibbard. |  |
| D | The Sisters of Mercy | Leeds gothic-rock band built around a drum machine called Doktor Avalanche. |  |
| E | Deep Purple | Hard-rock pioneers behind a famous riff about a fire on Lake Geneva. |  |
| F | The Doors | Los Angeles band whose singer styled himself the Lizard King. | **INTRUDER** |
| G | The Rolling Stones | London blues-rock band fronted by Mick Jagger for six decades. |  |
| H | Judas Priest | Birmingham metal band known for twin lead guitars and leather-and-studs. |  |
| I | Duran Duran | Birmingham new-wave band famous for glossy, exotic music videos. | **INTRUDER** |
| J | Pretenders | Chrissie Hynde's band, formed in London in the late 1970s. |  |

- **F The Doors**: Named after Aldous Huxley's book 'The Doors of Perception', which is a book, not a song.
- **I Duran Duran**: Named after a villain in the film 'Barbarella', which is a film, not a song.

## 10. [subtle] tools: `tools-named-for-true-inventor`

**Hidden theme:** Objects named after the person who actually invented them.  
**Decoy (what the intruders also satisfy):** Eponymous objects, meaning things named after a person  
**answer:** `G,H`

| ID | Item | Description | |
|---|---|---|---|
| A | Petri dish | Shallow lidded glass dish for growing cultures. |  |
| B | Diesel engine | Compression-ignition engine that runs without a spark plug. |  |
| C | Braille | Tactile writing system of raised dots. |  |
| D | Zeppelin | Rigid airship with gas cells inside a metal frame. |  |
| E | Jacuzzi | Hot tub whose jets pump bubbling water. |  |
| F | Stetson | Wide-brimmed felt hat associated with the American West. |  |
| G | Guillotine | Tall frame whose weighted, angled blade drops between two uprights. | **INTRUDER** |
| H | Cardigan | Knitted sweater that opens down the front with buttons. | **INTRUDER** |
| I | Tupperware | Plastic food containers with an airtight 'burping' seal. |  |
| J | Ferris wheel | Giant upright rotating wheel carrying passenger cars. |  |

- **G Guillotine**: Named after Joseph-Ignace Guillotin, who argued for its use but did not design it. Antoine Louis and Tobias Schmidt built it.
- **H Cardigan**: Named after the 7th Earl of Cardigan, who made it fashionable but did not invent it.
