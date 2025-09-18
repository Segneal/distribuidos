import { useCallback, useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext.jsx';
import { apiRequest } from '../services/apiClient.js';

const dateFormatter = new Intl.DateTimeFormat('es-AR', {
  dateStyle: 'full',
  timeStyle: 'short',
});

function formatDate(value) {
  if (!value) return 'Sin fecha definida';
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return dateFormatter.format(date);
  } catch (error) {
    return value;
  }
}

function Eventos() {
  const { token, user } = useAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [actionState, setActionState] = useState({});

  const fetchEvents = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    setFeedback(null);
    try {
      const data = await apiRequest('/api/eventos', { token });
      setEvents(Array.isArray(data?.eventos) ? data.eventos : []);
    } catch (err) {
      console.error('No se pudieron cargar los eventos', err);
      setError(err.message || 'No se pudieron cargar los eventos. Intentá nuevamente más tarde.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const isParticipating = (evento) => {
    if (!user) return false;
    return (evento.participantesIds || []).some((id) => Number(id) === Number(user.id));
  };

  const updateParticipants = (eventoId, updater) => {
    setEvents((prev) =>
      prev.map((evento) => {
        if (evento.id !== eventoId) return evento;
        const current = Array.isArray(evento.participantesIds) ? [...evento.participantesIds] : [];
        const updated = updater(current).map((id) => Number(id));
        return { ...evento, participantesIds: Array.from(new Set(updated)) };
      }),
    );
  };

  const withActionState = async (eventoId, action, callback) => {
    setActionState((prev) => ({ ...prev, [eventoId]: action }));
    setFeedback(null);
    try {
      await callback();
    } catch (err) {
      console.error('Acción sobre evento fallida', err);
      const message = err.details?.mensaje || err.message || 'No se pudo completar la acción.';
      setError(message);
      throw err;
    } finally {
      setActionState((prev) => {
        const { [eventoId]: _ignored, ...rest } = prev;
        return rest;
      });
    }
  };

  const handleJoin = async (eventoId) => {
    if (!user) return;
    await withActionState(eventoId, 'join', async () => {
      await apiRequest(`/api/eventos/${eventoId}/participantes`, {
        method: 'POST',
        token,
        body: { usuarioId: user.id },
      });
      updateParticipants(eventoId, (current) => [...current, user.id]);
      setFeedback('Te agregaste al evento exitosamente.');
    });
  };

  const handleLeave = async (eventoId) => {
    if (!user) return;
    await withActionState(eventoId, 'leave', async () => {
      await apiRequest(`/api/eventos/${eventoId}/participantes/${user.id}`, {
        method: 'DELETE',
        token,
      });
      updateParticipants(eventoId, (current) => current.filter((id) => Number(id) !== Number(user.id)));
      setFeedback('Te quitaste del evento.');
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-800">Eventos solidarios</h1>
          <p className="text-sm text-slate-600">
            Consultá la lista de actividades programadas y administrá tu participación de acuerdo al rol asignado.
          </p>
        </div>
        <button
          type="button"
          onClick={fetchEvents}
          className="rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm transition hover:border-primary-200 hover:text-primary-700"
        >
          Actualizar
        </button>
      </div>

      {feedback && (
        <div className="rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
          {feedback}
        </div>
      )}

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex min-h-[40vh] items-center justify-center text-slate-500">Cargando eventos…</div>
      ) : events.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
          Aún no hay eventos registrados.
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {events.map((evento) => {
            const participando = isParticipating(evento);
            const participantes = Array.isArray(evento.participantesIds) ? evento.participantesIds.length : 0;
            const action = actionState[evento.id];

            return (
              <article key={evento.id} className="flex h-full flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="space-y-3">
                  <h2 className="text-xl font-semibold text-primary-700">{evento.nombre}</h2>
                  <p className="text-sm text-slate-600">{evento.descripcion}</p>
                  <div className="rounded-md bg-slate-100 px-3 py-2 text-xs font-medium uppercase tracking-wide text-slate-600">
                    {formatDate(evento.fechaHora)}
                  </div>
                </div>

                <div className="mt-4 space-y-3 text-sm text-slate-600">
                  <p>
                    <span className="font-semibold text-slate-700">Participantes actuales:</span> {participantes}
                  </p>
                  {evento.donacionesRepartidas?.length ? (
                    <details className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
                      <summary className="cursor-pointer text-sm font-medium text-slate-700">Donaciones registradas</summary>
                      <ul className="mt-2 list-inside list-disc space-y-1 text-xs text-slate-600">
                        {evento.donacionesRepartidas.map((donacion, index) => (
                          <li key={`${evento.id}-don-${index}`}>
                            {donacion.descripcion || 'Donación'} — {donacion.categoria || 'Sin categoría'}
                          </li>
                        ))}
                      </ul>
                    </details>
                  ) : (
                    <p className="text-xs text-slate-400">Sin donaciones registradas todavía.</p>
                  )}
                </div>

                <div className="mt-6 flex items-center justify-between border-t border-slate-100 pt-4">
                  <span
                    className={`text-xs font-semibold uppercase tracking-wide ${
                      participando ? 'text-green-600' : 'text-slate-400'
                    }`}
                  >
                    {participando ? 'Participando' : 'Sin participación'}
                  </span>
                  <div className="flex gap-2">
                    {participando ? (
                      <button
                        type="button"
                        onClick={() => handleLeave(evento.id)}
                        disabled={action === 'leave'}
                        className="rounded-md border border-red-200 px-4 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:border-red-100 disabled:text-red-300"
                      >
                        {action === 'leave' ? 'Quitando…' : 'Quitarme'}
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleJoin(evento.id)}
                        disabled={action === 'join'}
                        className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-primary-300"
                      >
                        {action === 'join' ? 'Agregando…' : 'Sumarme'}
                      </button>
                    )}
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Eventos;
