import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import sessionService from '../services/sessionService';
import { reportService } from '../services/reportService';
import { Camera, CheckCircle, AlertCircle, Users, Clock } from 'lucide-react';

const ActiveSession = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [status, setStatus] = useState({ state: 'IDLE', info: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInit = async () => {
      try {
        const sess = await sessionService.getById(id);
        setSession(sess);
        const att = await sessionService.getAttendance(id);
        setAttendance(att);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchInit();
  }, [id]);

  useEffect(() => {
    if (!session || session.status !== 'ACTIVE') return;

    const interval = setInterval(async () => {
      try {
        const stat = await sessionService.getStatus(id);
        setStatus(stat);
        
        // Refresh attendance if verified recently
        if (stat.state === 'VERIFIED') {
          const att = await sessionService.getAttendance(id);
          setAttendance(att);
        }
      } catch (err) {
        // console.error(err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [session, id]);

  const handleEnd = async () => {
    if (window.confirm("Are you sure you want to end this attendance session?")) {
      try {
        const res = await sessionService.end(id);
        setSession(res);
      } catch (err) {
        console.error(err);
      }
    }
  };

  const getStatusMessage = (state) => {
    switch (state) {
      case 'SCANNING': return "Please look at the camera";
      case 'FACE_DETECTED': return "Face detected";
      case 'QUALITY_CHECK': return "Checking image quality";
      case 'RECOGNIZING': return "Recognizing...";
      case 'MULTI_FRAME_VERIFY': return "Verifying identity...";
      case 'VERIFIED': return "Attendance verified";
      case 'ALREADY_MARKED': return "Attendance already recorded";
      case 'UNKNOWN': return "Student not recognized";
      case 'LOW_QUALITY': return "Please improve lighting or move closer";
      case 'MULTIPLE_FACES': return "Please ensure only one student is visible";
      case 'CAMERA_ERROR': return "Camera unavailable";
      default: return "Initializing AI Engine...";
    }
  };

  if (loading) return <div className="p-8">Loading session...</div>;
  if (!session) return <div className="p-8">Session not found</div>;

  const presentCount = attendance.filter(a => a.status === 'PRESENT').length;
  const lateCount = attendance.filter(a => a.status === 'LATE').length;
  // Absent count for MVP is total - present - late (if we had total students). 
  // Let's just show what we have in DB.

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col md:flex-row gap-8">
      {/* LEFT: Camera Viewer */}
      <div className="md:w-2/3 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Camera size={20} /> Live Camera
            </h2>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              session.status !== 'ACTIVE' ? 'bg-gray-100 text-gray-600' :
              status.state === 'CAMERA_ERROR' ? 'bg-red-100 text-red-600' :
              'bg-red-100 text-red-600 animate-pulse'
            }`}>
              {session.status !== 'ACTIVE' ? 'OFFLINE' : 
               status.state === 'CAMERA_ERROR' ? '🔴 DISCONNECTED' : '● LIVE'}
            </span>
          </div>
          <div className="bg-gray-900 aspect-video relative flex items-center justify-center">
            {session.status === 'ACTIVE' && session.stream_token ? (
              <img 
                src={`http://localhost:8000/api/sessions/${session.id}/stream/?token=${session.stream_token}`} 
                alt="Live Feed" 
                className="w-full h-full object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'block';
                }}
              />
            ) : (
              <div className="text-gray-500 flex flex-col items-center">
                <Camera size={48} className="mb-2 opacity-50" />
                <p>Camera is offline</p>
              </div>
            )}
            <div className="hidden text-white absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">Stream Unavailable</div>
          </div>
          <div className="p-6 bg-gray-50">
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-full ${
                status.state === 'VERIFIED' ? 'bg-green-100 text-green-600' :
                status.state === 'UNKNOWN' ? 'bg-red-100 text-red-600' :
                status.state === 'MULTI_FRAME_VERIFY' ? 'bg-yellow-100 text-yellow-600' :
                'bg-blue-100 text-blue-600'
              }`}>
                {status.state === 'VERIFIED' ? <CheckCircle size={24} /> : <AlertCircle size={24} />}
              </div>
              <div className="flex-1">
                <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Status: {status.state}</p>
                <p className="text-xl font-medium text-gray-900">{getStatusMessage(status.state)}</p>
                
                {status.state === 'MULTI_FRAME_VERIFY' && status.info && (
                  <div className="mt-2 text-sm text-yellow-700">
                    Verification {status.info.match_count} / {status.info.required} (Distance: {status.info.distance.toFixed(3)})
                  </div>
                )}
                
                {status.state === 'VERIFIED' && status.info && (
                  <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800">
                    <p className="font-bold text-lg">✓ {status.info.student_name}</p>
                    <p className="text-sm opacity-80">Recognition distance: {status.info.distance.toFixed(3)}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT: Attendance Summary */}
      <div className="md:w-1/3 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-1">{session.subject}</h2>
          <p className="text-gray-500 mb-6">{new Date(session.created_at).toLocaleDateString()}</p>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded-lg text-center border border-green-100">
              <p className="text-3xl font-bold text-green-700">{presentCount}</p>
              <p className="text-sm font-medium text-green-600">Present</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg text-center border border-yellow-100">
              <p className="text-3xl font-bold text-yellow-700">{lateCount}</p>
              <p className="text-sm font-medium text-yellow-600">Late</p>
            </div>
          </div>
          
          {session.status === 'ACTIVE' ? (
            <button 
              onClick={handleEnd}
              className="w-full py-3 bg-red-600 text-white rounded-lg font-bold hover:bg-red-700 transition-colors"
            >
              END SESSION
            </button>
          ) : (
            <div className="space-y-3">
              <div className="w-full py-3 bg-gray-100 text-gray-600 rounded-lg font-bold text-center border border-gray-200">
                ATTENDANCE COMPLETED
              </div>
              <button
                onClick={() => reportService.exportSessionCSV(id)}
                className="w-full py-2 border border-indigo-600 text-indigo-600 rounded-lg font-bold hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2"
              >
                Download CSV Report
              </button>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex-1 flex flex-col overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Recent Attendance</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {attendance.slice().reverse().map(record => (
              <div key={record.id} className="flex justify-between items-center p-3 hover:bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                    {record.student_name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{record.student_name}</p>
                    <p className="text-xs text-gray-500">{new Date(record.marked_at).toLocaleTimeString()}</p>
                  </div>
                </div>
                <span className={`text-xs font-bold px-2 py-1 rounded ${
                  record.status === 'PRESENT' ? 'bg-green-100 text-green-700' : 
                  record.status === 'LATE' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                }`}>
                  {record.status}
                </span>
              </div>
            ))}
            {attendance.length === 0 && (
              <p className="text-center text-gray-500 py-8">No attendance recorded yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ActiveSession;
