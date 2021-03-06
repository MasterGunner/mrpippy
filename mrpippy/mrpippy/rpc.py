
import json

class RequestType(object):
	UseItem = 0 
	DropItem = 1 
	SetFavorite = 2 
	ToggleComponentFavorite = 3 
	SortInventory = 4 
	ToggleQuestActive = 5 
	SetCustomMapMarker = 6 
	RemoveCustomMapMarker = 7 
	CheckFastTravel = 8 
	FastTravel = 9 
	MoveLocalMap = 10
	ZoomLocalMap = 11
	ToggleRadioStation = 12
	RequestLocalMapSnapshot = 13
	ClearIdle = 14


class LocationMarkerType(object):
	CaveMarker = 0
	CityMarker = 1
	DiamondCityMarker = 2
	EncampmentMarker = 3
	FactoryMarker = 4
	MonumentMarker = 5
	MetroMarker = 6
	MilitaryBaseMarker = 7
	LandmarkMarker = 8
	OfficeMarker = 9
	TownRuinsMarker = 10
	UrbanRuinsMarker = 11
	SancHillsMarker = 12
	SettlementMarker = 13
	SewerMarker = 14
	VaultMarker = 15
	AirfieldMarker = 16
	BunkerHillMarker = 17
	CamperMarker = 18
	CarMarker = 19
	ChurchMarker = 20
	CountryClubMarker = 21
	CustomHouseMarker = 22
	DriveInMarker = 23
	ElevatedHighwayMarker = 24
	FaneuilHallMarker = 25
	FarmMarker = 26
	FillingStationMarker = 27
	ForestedMarker = 28
	GoodneighborMarker = 29
	GraveyardMarker = 30
	HospitalMarker = 31
	IndustrialDomeMarker = 32
	IndustrialStacksMarker = 33
	InstituteMarker = 34
	IrishPrideMarker = 35
	JunkyardMarker = 36
	ObservatoryMarker = 37
	PierMarker = 38
	PondLakeMarker = 39
	QuarryMarker = 40
	RadioactiveAreaMarker = 41
	RadioTowerMarker = 42
	SalemMarker = 43
	SchoolMarker = 44
	ShipwreckMarker = 45
	SubmarineMarker = 46
	SwanPondMarker = 47
	SynthHeadMarker = 48
	TownMarker = 49
	BoSMarker = 50
	BrownstoneMarker = 51
	BunkerMarker = 52
	CastleMarker = 53
	SkyscraperMarker = 54
	LibertaliaMarker = 55
	LowRiseMarker = 56
	MinutemenMarker = 57
	PoliceStationMarker = 58
	PrydwenMarker = 59
	RailroadFactionMarker = 60
	RailroadMarker = 61
	SatelliteMarker = 62
	SentinelMarker = 63
	USSConstitutionMarker = 64
	DoorMarker = 65
	QuestMarker = 66
	QuestMarkerDoor = 67
	QuestMarker = 68
	PlayerSetMarker = 69
	PlayerLocMarker = 70
	PowerArmorLocMarker = 71


class RPCManager(object):
	"""Manager for client RPC calls. Keeps track of what has been answered and
	executes callback(response dict) when it gets a response."""
	def __init__(self):
		self.next_id = 0
		self.outstanding = {} # maps id: callback

	def allocate_id(self):
		current = self.next_id
		self.next_id += 1
		return current

	def create_request(self, callback, request_type, *args):
		request = {
			'id': self.allocate_id(),
			'type': request_type,
			'args': args,
		}
		self.outstanding[request['id']] = callback
		return json.dumps(request)

	def recv(self, response):
		response = json.loads(response)
		if response['id'] not in self.outstanding:
			raise ValueError("Response for unknown id {}: {}".format(response['id']), response)
		self.outstanding.pop(response['id'])(response)

	# specific methods for creating requests

	def use_item(self, callback, handle_id, version):
		"""Use item with given handle id from inventory.
		eg. consume aid, or equip weapon.
		Version is likely a means to avoid race conditions, assumedly must be current."""
		return self.create_request(callback, RequestType.UseItem, handle_id, 0, version)

	def toggle_radio_station(self, index):
		"""Activate radio station with given index in the list of radio stations.
		If already active, deactivate it instead, leaving no station on."""
		return self.create_request(callback, RequestType.ToggleRadioStation, index)


class RPCServer(object):
	"""Helper for responding to RPC calls as the server.
	Automatically dispatches incoming requests to the appropriate method.
	Method defaults will return reasonable "no-ops" where applicable.
	It is intended that you override these with meaningful implementations.
	"""
	# map from RequestType to the method name
	DISPATCH = {
		RequestType.UseItem: 'use_item',
		RequestType.DropItem: 'drop_item',
		RequestType.SetFavorite: 'set_favorite',
		RequestType.ToggleComponentFavorite: 'toggle_component_favorite',
		RequestType.SortInventory: 'sort_inventory',
		RequestType.ToggleQuestActive: 'toggle_quest_active',
		RequestType.SetCustomMapMarker: 'set_custom_map_marker',
		RequestType.RemoveCustomMapMarker: 'remove_custom_map_marker',
		RequestType.CheckFastTravel: 'check_fast_travel',
		RequestType.FastTravel: 'fast_travel',
		RequestType.MoveLocalMap: 'move_local_map',
		RequestType.ZoomLocalMap: 'zoom_local_map',
		RequestType.ToggleRadioStation: 'toggle_radio_station',
		RequestType.RequestLocalMapSnapshot: 'request_local_map_snapshot',
		RequestType.ClearIdle: 'clear_idle',
	}

	def get_response(self, request):
		request = json.loads(request)
		id = request.pop('id')
		method = getattr(self, self.DISPATCH[request['type']])
		response = method(*request['args'])
		response['id'] = id
		return response

	# TODO
