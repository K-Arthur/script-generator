import React from 'react';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import ScriptEditor from './components/ScriptEditor';

function App() {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Script Generator
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <ScriptEditor />
      </Container>
    </Box>
  );
}

export default App;
