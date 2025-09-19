import api from './index';
export const getEventos = async () => (await api.get('/eventos')).data;
export const createEvento = async (payload) => (await api.post('/eventos', payload)).data;
export const updateEvento = async (id, payload) => (await api.put('/eventos/' + id, payload)).data;
export const deleteEvento = async (id) => (await api.delete('/eventos/' + id)).data;
export const toggleParticipation = async (id) => (await api.post(`/eventos/${id}/participar`)).data;
