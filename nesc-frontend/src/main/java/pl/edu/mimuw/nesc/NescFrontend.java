package pl.edu.mimuw.nesc;

import com.google.common.base.Optional;
import org.apache.commons.cli.ParseException;
import org.apache.log4j.Logger;
import pl.edu.mimuw.nesc.exception.InvalidOptionsException;
import pl.edu.mimuw.nesc.option.OptionsHolder;
import pl.edu.mimuw.nesc.option.OptionsParser;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.google.common.base.Preconditions.checkNotNull;

/**
 * Frontend implementation for nesc language.
 *
 * @author Grzegorz Kołakowski <gk291583@students.mimuw.edu.pl>
 */
public final class NescFrontend implements Frontend {

    private static final Logger LOG = Logger.getLogger(NescFrontend.class);

    public static Builder builder() {
        return new Builder();
    }

    private final boolean isStandalone;
    private final Map<ContextRef, FrontendContext> contextsMap;

    private NescFrontend(Builder builder) {
        this.isStandalone = builder.isStandalone;
        this.contextsMap = new HashMap<>();
    }

    @Override
    public ContextRef createContext(String[] args) throws InvalidOptionsException {
        checkNotNull(args, "arguments cannot be null");
        LOG.info("Create context; " + Arrays.toString(args));

        final ContextRef contextRef = new ContextRef();
        final FrontendContext context = createContextWorker(args);
        this.contextsMap.put(contextRef, context);

        rebuild(contextRef);

        return contextRef;
    }

    @Override
    public ProjectData rebuild(ContextRef contextRef) {
        checkNotNull(contextRef, "context reference cannot be null");
        LOG.info("Rebuild; contextRef=" + contextRef);

        final FrontendContext context = getContext(contextRef).basicCopy();
        setContext(context, contextRef);

        final Optional<String> startFile = context.getPathsResolver()
                .getEntityFile(context.getOptions().getEntryEntity());

        // FIXME exception
        try {
            parseFilesIncludedByDefault(context);
        } catch (IOException e) {
            e.printStackTrace();
        }

        update(contextRef, startFile.get());

        final ProjectData result = new ProjectData();
        for (Map.Entry<String, FileCache> entry : context.getCache().entrySet()) {
            result.addFile(FileData.convertFrom(entry.getValue()));
        }

        return result;
    }

    @Override
    public FileData update(ContextRef contextRef, String filePath) {
        checkNotNull(contextRef, "context reference cannot be null");
        checkNotNull(filePath, "file path cannot be null");
        LOG.info("Update; contextRef=" + contextRef + "; filePath=" + filePath);

        final FrontendContext context = getContext(contextRef);

        try {
            new ParseExecutor(context).parse(filePath, true);
            /*
             * File data is created only when necessary (to avoid creating
             * costly objects that might not be used).
             */
            return FileData.convertFrom(context.getCache().get(filePath));
        } catch (IOException e) {
            // TODO
            e.printStackTrace();
        }
        // FIXME FileData should be always returned or proper exception
        // should be thrown.
        return null;
    }

    private FrontendContext getContext(ContextRef contextRef) {
        final FrontendContext context = this.contextsMap.get(contextRef);
        if (context == null) {
            throw new IllegalArgumentException("unknown context reference");
        }
        return context;
    }

    private void setContext(FrontendContext context, ContextRef contextRef) {
        this.contextsMap.put(contextRef, context);
    }

    /**
     * Creates context worker from given options.
     *
     * @param args unstructured options
     * @return context worker
     * @throws InvalidOptionsException thrown when context options cannot be
     *                                 parsed successfully
     */
    private FrontendContext createContextWorker(String[] args) throws InvalidOptionsException {
        final OptionsParser optionsParser = new OptionsParser();
        final FrontendContext result;
        try {
            final OptionsHolder options = optionsParser.parse(args);
            result = new FrontendContext(options);
            return result;
        } catch (ParseException e) {
            final String msg = e.getMessage();
            if (this.isStandalone) {
                System.out.println(msg);
                optionsParser.printHelp();
                System.exit(1);
                return null;
            } else {
                throw new InvalidOptionsException(msg);
            }
        } catch (IOException e) {
            if (this.isStandalone) {
                e.printStackTrace();
                System.exit(1);
                return null;
            } else {
                final String msg = "Cannot find options.properties file.";
                throw new IllegalStateException(msg);
            }
        }
    }

    private void parseFilesIncludedByDefault(FrontendContext context) throws IOException {
        final List<String> defaultIncludes = context.getDefaultIncludeFiles();

        for (String filePath : defaultIncludes) {
            new ParseExecutor(context).parse(filePath, false);
        }
    }


    /**
     * Nesc frontend builder.
     */
    public static final class Builder {

        private boolean isStandalone;

        public Builder() {
            this.isStandalone = false;
        }

        /**
         * Sets whether frontend is standalone or used as a library.
         * By default is not standalone.
         *
         * @param standalone is standalone
         * @return builder
         */
        public Builder standalone(boolean standalone) {
            this.isStandalone = standalone;
            return this;
        }

        public NescFrontend build() {
            verify();
            return new NescFrontend(this);
        }

        private void verify() {
        }

    }

}