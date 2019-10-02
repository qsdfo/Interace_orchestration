function Clip(path) {
  this.liveObject = new LiveAPI(path);
}
 
Clip.prototype.getLength = function() {
  return this.liveObject.get('length');
}

Clip.prototype.getNotes = function(startTime, timeRange, startPitch, pitchRange) {
  return this.liveObject.call("get_notes", startTime, startPitch, timeRange, pitchRange);
}

Clip.prototype.setNotes = function(notes) {
  var liveObject = this.liveObject;
  liveObject.call("set_notes");
  liveObject.call("notes", notes.length);
  notes.forEach(function(note) {
    liveObject.call("note", note.pitch,
                    note.start.toFixed(4), note.duration.toFixed(4),
                    note.velocity, note.muted);
  });
  liveObject.call("done");
}

function Note(pitch, start, duration, velocity, muted) {
  this.pitch = pitch;
  this.start = start;
  this.duration = duration;
  this.velocity = velocity;
  this.muted = muted;
}
 
Note.prototype.toString = function() {
  return '{pitch:' + this.pitch +
         ', start:' + this.start +
         ', duration:' + this.duration +
         ', velocity:' + this.velocity +
         ', muted:' + this.muted + '}';
}

// Send a list of notes to the right midi track
function list(a) {
	track_index = arguments[0]
	var path = "live_set tracks "
  	path = path.concat(String(track_index))
 	path = path.concat(" clip_slots 0 clip")
	clip = new Clip(path);
	notes = [];
	for(var i=1,len=arguments.length-1; i<len; i+=3) {
  		// each note starts with "note" (which we ignore) and is 6 items in the list
  		var note = new Note(arguments[i], arguments[i+1], arguments[i+2], 80, 0);
  		notes.push(note);
	}
	clip.setNotes(notes)
}

// Clear all orchestral tracks (called just before a new orchestration is requested to Python server)
function clear_tracks(max_length){
	for(var track_index=1, len=15; track_index<len; track_index+=1) {
		var path = "live_set tracks ";
  		path = path.concat(String(track_index));
		path = path.concat(" clip_slots 0");
		clip_slot = new LiveAPI(path);
		// Don't know why but has_clip doesn't work... get undefined
		// post(clip_slot.has_clip)
		try {
			clip_slot.call("delete_clip");
		} catch(e) {}
		try {
			clip_slot.call("create_clip", max_length)
		} catch(e) {}
	}
}