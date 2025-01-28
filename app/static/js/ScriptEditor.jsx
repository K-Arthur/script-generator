import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  LinearProgress,
  Paper,
  Grid,
  Alert,
} from '@mui/material';

const ScriptEditor = () => {
  const [content, setContent] = useState('');
  const [highlightedConcept, setHighlightedConcept] = useState('');
  const [previousTopic, setPreviousTopic] = useState('');
  const [script, setScript] = useState('');
  const [validation, setValidation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const pollInterval = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload-file', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.status === 'success') {
        setContent(data.content);
      } else {
        setError('Error uploading file');
      }
    } catch (err) {
      setError('Error uploading file: ' + err.message);
    }
  };

  const generateScript = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/generate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          highlighted_concept: highlightedConcept,
          previous_topic: previousTopic,
        }),
      });

      const data = await response.json();
      if (data.task_id) {
        // Start polling for results
        pollInterval.current = setInterval(
          () => checkScriptStatus(data.task_id),
          2000
        );
      } else {
        setError('Error generating script');
        setLoading(false);
      }
    } catch (err) {
      setError('Error generating script: ' + err.message);
      setLoading(false);
    }
  };

  const checkScriptStatus = async (taskId) => {
    try {
      const response = await fetch(`/api/script-status/${taskId}`);
      const data = await response.json();

      if (data.status === 'completed') {
        clearInterval(pollInterval.current);
        setScript(data.script);
        setValidation(data.validation);
        setLoading(false);
      } else if (data.status === 'failed') {
        clearInterval(pollInterval.current);
        setError(data.error);
        setLoading(false);
      }
    } catch (err) {
      clearInterval(pollInterval.current);
      setError('Error checking script status: ' + err.message);
      setLoading(false);
    }
  };

  const validateScript = async () => {
    try {
      const response = await fetch('/api/validate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ script }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setValidation(data.validation);
      }
    } catch (err) {
      setError('Error validating script: ' + err.message);
    }
  };

  useEffect(() => {
    return () => {
      if (pollInterval.current) {
        clearInterval(pollInterval.current);
      }
    };
  }, []);

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Script Generator
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Input
              </Typography>

              <Button
                variant="contained"
                component="label"
                sx={{ mb: 2 }}
              >
                Upload File
                <input
                  type="file"
                  hidden
                  onChange={handleFileUpload}
                  accept=".txt,.doc,.docx"
                />
              </Button>

              <TextField
                fullWidth
                multiline
                rows={10}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter your content here..."
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                value={highlightedConcept}
                onChange={(e) => setHighlightedConcept(e.target.value)}
                label="Highlighted Concept"
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                value={previousTopic}
                onChange={(e) => setPreviousTopic(e.target.value)}
                label="Previous Topic"
                sx={{ mb: 2 }}
              />

              <Button
                variant="contained"
                onClick={generateScript}
                disabled={loading || !content}
                fullWidth
              >
                Generate Script
              </Button>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Generated Script
              </Typography>

              {loading && <LinearProgress sx={{ mb: 2 }} />}

              <TextField
                fullWidth
                multiline
                rows={15}
                value={script}
                onChange={(e) => setScript(e.target.value)}
                sx={{ mb: 2 }}
              />

              <Button
                variant="outlined"
                onClick={validateScript}
                disabled={!script}
                fullWidth
              >
                Validate Script
              </Button>

              {validation && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Validation Results
                  </Typography>
                  {Object.entries(validation).map(([key, value]) => (
                    <Box key={key} sx={{ mb: 1 }}>
                      <Typography variant="body2">
                        {key}: {value.pass ? '✅' : '❌'} (
                        {value.value.toFixed(2)} / {value.threshold})
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ScriptEditor;
