import { createSlice } from '@reduxjs/toolkit';  

export const chatSlice = createSlice({  
  name: 'chat',  
  initialState: {  
    messages: []  
  },  
  reducers: {  
    sendMessage: (state, action) => {  
      state.messages.push(action.payload);  
    }  
  }  
});  

export const { sendMessage } = chatSlice.actions;  
export default chatSlice.reducer;