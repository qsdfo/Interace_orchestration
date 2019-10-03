inlets = 1;
outlets = 1;

function Clip(clip_number) {
  	var path = "this_device canonical_parent clip_slots ".concat(clip_number, " clip");
	this.liveObject = new LiveAPI(path);
}
 
Clip.prototype.getLength = function() {
  return this.liveObject.get('length');
}

Clip.prototype.getNotes = function(startTime, timeRange, startPitch, pitchRange) {
  return this.liveObject.call("get_notes", startTime, startPitch, timeRange, pitchRange);
}

function load_clip(clip_number) {
	var clip = new Clip(clip_number);
	var length = clip.getLength()
	post(length)
	var notes = clip.getNotes(0, length, 0, 128)
	outlet(0, notes, length)
}