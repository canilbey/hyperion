CREATE TRIGGER update_chat_contexts_updated_at
    BEFORE UPDATE ON chat_contexts
    FOR EACH ROW
    EXECUTE FUNCTION update_chat_contexts_updated_at(); 