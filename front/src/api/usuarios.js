import api from './index';
export const getUsuarios = async () => (await api.get('/usuarios')).data;
export const createUsuario = async (payload) => (await api.post('/usuarios', payload)).data;
export const updateUsuario = async (id, payload) => (await api.put('/usuarios/' + id, payload)).data;
export const deleteUsuario = async (id) => (await api.delete('/usuarios/' + id)).data;
